import enum
import time
import typing

import botocore.client


def response_ok(response: dict):
    resp_meta = response['ResponseMetadata']
    if (status_code := resp_meta['HTTPStatusCode']) == 200:
        return response

    raise RuntimeError(f'rq {resp_meta["RequestId"]=} failed {status_code=}')


class TaskStatus(enum.Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    DELETED = 'deleted' # indicates an error (image was rejected)


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

    while not (status:= current_status()) is TaskStatus.COMPLETED:
        print(f'{snapshot_task_id=}: {status=}')

        if status is TaskStatus.DELETED:
            raise RuntimeError(f'image uploaded by {snapshot_task_id=} was rejected')
        time.sleep(polling_interval_seconds)

    return snapshot_id()


def register_image(
    ec2_client: 'botocore.client.EC2',
    snapshot_id: str,
    image_name: str,
) -> str:
    '''
    @return: ami-id of registered image
    '''
    root_device_name = '/dev/xvda'

    result = ec2_client.register_image(
        # ImageLocation=XX, s3-url?
        Architecture='x86_64', # | i386, arm64
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
        VirtualizationType='hvm', # | paravirtual
    )

    # XXX need to wait until image is available (before publishing)
    return result['ImageId']


def enumerate_region_names(
    ec2_client: 'botocore.client.EC2',
):
    for region in ec2_client.describe_regions()['Regions']:
        yield region['RegionName']


def set_image_public(
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
