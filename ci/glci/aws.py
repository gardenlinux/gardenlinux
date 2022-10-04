import concurrent.futures
import dataclasses
import enum
import logging
import pprint
import time
import typing

import botocore.client

import glci.model
import glci.util


logger = logging.getLogger(__name__)


def response_ok(response: dict):
    resp_meta = response['ResponseMetadata']
    if (status_code := resp_meta['HTTPStatusCode']) == 200:
        return response

    raise RuntimeError(f'rq {resp_meta["RequestId"]=} failed {status_code=}')


class TaskStatus(enum.Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    DELETED = 'deleted' # indicates an error (image was rejected)


class ImageState(enum.Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    INVALID = 'invalid'
    DEREGISTERED = 'deregistered'
    TRANSIENT = 'transient'
    FAILED = 'failed'
    ERROR = 'error'

    def is_erroneous(self):
        if self in (
            ImageState.INVALID,
            ImageState.FAILED,
            ImageState.ERROR,
        ):
            return True
        else:
            return False


def import_snapshot(
    ec2_client: 'botocore.client.EC2',
    s3_bucket_name: str,
    image_key: str,
) -> str:
    '''
    @return import_task_id (use for `wait_for_snapshot_import`)
    '''
    res = ec2_client.import_snapshot(
        ClientData={
            'Comment': 'uploaded by gardenlinux-cicd',
        },
        Description='uploaded by gardenlinux-cicd',
        DiskContainer={
            'UserBucket': {
                'S3Bucket': s3_bucket_name,
                'S3Key': image_key,
            },
            'Format': 'raw',
            'Description': 'uploaded by gardenlinux-cicd',
        },
    )

    import_task_id = res['ImportTaskId']
    return import_task_id


def wait_for_snapshot_import(
    ec2_client: 'botocore.client.EC2',
    snapshot_task_id: str,
    polling_interval_seconds: int=15,
):
    '''
    @return snapshot_id
    '''
    def describe_import_snapshot_task():
        status = ec2_client.describe_import_snapshot_tasks(
            ImportTaskIds=[snapshot_task_id]
        )['ImportSnapshotTasks'][0]
        return status

    def current_status() -> TaskStatus:
        status = describe_import_snapshot_task()
        status = TaskStatus(status['SnapshotTaskDetail']['Status'])
        return status

    def snapshot_id():
        status = describe_import_snapshot_task()
        task_id = status['SnapshotTaskDetail']['SnapshotId']
        return task_id

    while not (status := current_status()) is TaskStatus.COMPLETED:
        logger.info(f'{snapshot_task_id=}: {status=}')

        if status is TaskStatus.DELETED:
            raise RuntimeError(f'image uploaded by {snapshot_task_id=} was rejected')
        time.sleep(polling_interval_seconds)

    return snapshot_id()


def _to_aws_architecture(
    architecture: glci.model.Architecture,
) -> str:
    '''Convert the Value of our Architecture-enum to the values AWS knows/expects
    '''
    match architecture:
        case glci.model.Architecture.AMD64:
            return 'x86_64'
        case glci.model.Architecture.ARM64:
            return 'arm64'
        case _:
            raise NotImplementedError(architecture)


def register_image(
    ec2_client: 'botocore.client.EC2',
    snapshot_id: str,
    image_name: str,
    architecture: str,
) -> str:
    '''
    @return: ami-id of registered image
    '''
    root_device_name = '/dev/xvda'

    result = ec2_client.register_image(
        # ImageLocation=XX, s3-url?
        Architecture=architecture,
        BlockDeviceMappings=[
            {
                'DeviceName': root_device_name,
                'Ebs': {
                    'DeleteOnTermination': True,
                    'SnapshotId': snapshot_id,
                    'VolumeType': 'gp2',
                }
            }
        ],
        Description='gardenlinux',
        EnaSupport=True,
        Name=image_name,
        RootDeviceName=root_device_name,
        VirtualizationType='hvm' # | paravirtual
    )

    ec2_client.create_tags(
        Resources=[
            result['ImageId'],
        ],
        Tags=[
            {
                'Key': 'sec-by-def-public-image-exception',
                'Value': 'enabled',
            },
        ]
    )

    # XXX need to wait until image is available (before publishing)
    return result['ImageId']


def enumerate_region_names(
    ec2_client: 'botocore.client.EC2',
):
    for region in ec2_client.describe_regions()['Regions']:
        yield region['RegionName']


def wait_for_image_state(
    ec2_client: 'botocore.client.EC2',
    image_id: str,
    target_state=ImageState.AVAILABLE,
    polling_interval_seconds: int=15,
):
    def current_image_state():
        image_details = ec2_client.describe_images(ImageIds=[image_id])['Images'][0]
        image_state = ImageState(image_details['State'])
        return image_state

    while not (image_state := current_image_state()) is target_state:
        if image_state.is_erroneous():
            raise RuntimeError(f'{image_id=}: {image_state=}')
        time.sleep(polling_interval_seconds)

    return image_state


def wait_for_images(
    mk_session: callable,
    region_img_map: typing.Dict[str, str], # {region_name: ami_id}
    target_state=ImageState.AVAILABLE,
):
    logger.info(f'will wait for {len(region_img_map)} image(s) to reach {target_state=}')
    for region_name, image_id in region_img_map.items():
        logger.info(f'waiting for {image_id=}')
        # as we want to wait for _all_ images, it should be OK not to parallelise polling
        image_state = wait_for_image_state(
            ec2_client=mk_session(region_name=region_name).client('ec2'),
            image_id=image_id,
            target_state=target_state,
        )
        logger.info(f'{image_id=} reached state {image_state=}')
    logger.info('all images reached target-state')


def set_images_public(
    mk_session: callable,
    region_img_map: typing.Dict[str, str], # {region_name: ami_id}
):
    for region_name, image_id in region_img_map.items():
        session = mk_session(region_name=region_name)
        ec2_client = session.client('ec2')

        res = ec2_client.modify_image_attribute(
            Attribute='launchPermission',
            ImageId=image_id,
            LaunchPermission={
                'Add': [
                    {
                        'Group': 'all',
                    },
                ],
            },
        )
        response_ok(res)


def copy_image(
    mk_session: callable,
    ami_image_id: str,
    image_name: str,
    src_region_name: str,
    target_regions: typing.Sequence[str],
):
    '''
    @param mk_session: callable accepting `region_name`, returning authenticated boto3-session
    '''
    for target_region in target_regions:
        if target_region == src_region_name:
            continue

        session = mk_session(region_name=target_region)
        ec2_client = session.client('ec2')

        res = ec2_client.copy_image(
            SourceImageId=ami_image_id,
            SourceRegion=src_region_name,
            Name=image_name,
        )
        # XXX: return (new) image-AMI
        response_ok(res)
        yield target_region, res['ImageId']


def image_ids_by_name(
    mk_session: callable,
    image_name: str,
    region_names: typing.Sequence[str],
):
    for region_name in region_names:
        session = mk_session(region_name=region_name)
        ec2 = session.client('ec2')
        images = ec2.describe_images(Filters=[{'Name': 'name', 'Values': [image_name]}])
        # there must either be one or none
        images = images['Images']
        if len(images) < 1:
            logger.warning(f'did not find {image_name=} in {region_name=}')
            continue
        if len(images) > 1:
            raise ValueError('found more than one image (this is a bug)')

        yield region_name, images[0]['ImageId']


def unregister_images_by_name(
    mk_session: callable,
    image_name: str,
    region_names: typing.Sequence[str]=None,
):
    if not region_names:
        ec2_client = mk_session().client('ec2')
        region_names = tuple(enumerate_region_names(ec2_client=ec2_client))
    else:
        region_names = tuple(region_names)

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(region_names))

    results = []
    for region_name, image_id in image_ids_by_name(
        mk_session=mk_session,
        image_name=image_name,
        region_names=region_names,
    ):
        def unregister_image():
            ec2 = mk_session(region_name=region_name).client('ec2')
            ec2.deregister_image(ImageId=image_id)
            logger.info(f'unregistered {image_id=}')
        results.append(executor.submit(unregister_image))

    concurrent.futures.wait(results)


def import_image(
    ec2_client: 'botocore.client.EC2',
    s3_bucket_name: str,
    image_key: str,
):
    '''
    triggers import-image

    note: if e.g. a uefi partition is detected, aws will reject image
    workaround: use import_snapshot (where no such validation is done)
    '''
    res = ec2_client.import_snapshot(
        ClientData={
            'Comment': 'uploaded by gardenlinux-cicd',
        },
        Description='uploaded by gardenlinux-cicd',
        DiskContainers=[{
            'UserBucket': {
                'S3Bucket': s3_bucket_name,
                'S3Key': image_key,
            },
            'Format': 'raw',
            'Description': 'uploaded by gardenlinux-cicd',
        }],
    )

    import_task_id = res['ImportTaskId']
    return import_task_id


def target_image_name_for_release(release: glci.model.OnlineReleaseManifest):
    target_image_name = f'gardenlinux-{release.canonical_release_manifest_key_suffix()}'
    return target_image_name


def upload_and_register_gardenlinux_image(
    mk_session: callable,
    build_cfg: glci.model.BuildCfg,
    release: glci.model.OnlineReleaseManifest,
) -> glci.model.OnlineReleaseManifest:
    session = mk_session(region_name=build_cfg.aws_region)
    ec2_client = session.client('ec2')

    target_image_name = target_image_name_for_release(release=release)

    aws_release_artifact = glci.util.virtual_image_artifact_for_platform('aws')
    aws_release_artifact_path = release.path_by_suffix(aws_release_artifact)

    # TODO: check path is actually S3_ReleaseFile
    raw_image_key = aws_release_artifact_path.s3_key
    bucket_name = aws_release_artifact_path.s3_bucket_name

    snapshot_task_id = import_snapshot(
        ec2_client=ec2_client,
        s3_bucket_name=bucket_name,
        image_key=raw_image_key,
    )
    logger.info(f'started import {snapshot_task_id=}')

    snapshot_id = wait_for_snapshot_import(
        ec2_client=ec2_client,
        snapshot_task_id=snapshot_task_id,
    )
    logger.info(f'import task finished {snapshot_id=}')

    initial_ami_id = register_image(
        ec2_client=ec2_client,
        snapshot_id=snapshot_id,
        image_name=target_image_name,
        architecture=_to_aws_architecture(release.architecture),
    )
    logger.info(f'registered {initial_ami_id=}')

    region_names = tuple(enumerate_region_names(ec2_client=ec2_client))

    try:
        image_map = dict(
            copy_image(
                mk_session=mk_session,
                ami_image_id=initial_ami_id,
                image_name=target_image_name,
                src_region_name=build_cfg.aws_region,
                target_regions=region_names,
            )
        )
    except:
        logger.warning('an error occurred whilst copying images - will remove them')
        unregister_images_by_name(
            mk_session=mk_session,
            image_name=target_image_name,
            region_names=region_names,
        )
        raise

    # dict{<region_name>: <ami_id>}

    # add origin image
    image_map[build_cfg.aws_region] = initial_ami_id

    published_images = tuple((
        glci.model.AwsPublishedImage(
            ami_id=ami_id,
            aws_region_id=region_name,
            image_name=target_image_name,
        ) for region_name, ami_id in image_map.items()
    ))
    published_image_set = glci.model.AwsPublishedImageSet(published_aws_images=published_images)

    image_map_pretty = pprint.pformat(image_map)
    logger.info(f'copied images: {image_map_pretty}')

    wait_for_images(
        mk_session=mk_session,
        region_img_map=image_map,
    )
    logger.info(f'all {len(image_map)} images became "ready"')

    set_images_public(
        mk_session=mk_session,
        region_img_map=image_map,
    )
    logger.info(f'all {len(image_map)} images were set to "public"')

    return dataclasses.replace(release, published_image_metadata=published_image_set)
