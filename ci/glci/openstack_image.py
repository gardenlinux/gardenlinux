import dataclasses
import functools
from datetime import datetime
from time import sleep

from openstack import connect

import glci

class OpenstackImageUploader:
    '''OpenstackImageUploader is a client to upload images to Openstack Glance.'''

    def __init__(self, openrc: glci.model.OpenstackEnviroment):
        self.openstack_env = openrc

    @functools.lru_cache
    def _get_connection(self):
        return connect(
            auth_url=self.openstack_env.auth_url,
            project_name=self.openstack_env.project_name,
            username=self.openstack_env.username,
            password=self.openstack_env.password,
            region_name=self.openstack_env.region,
            user_domain_name=self.openstack_env.domain,
            project_domain_name=self.openstack_env.domain,
        )

    def upload_image_from_fs(self, name: str, path: str, meta: dict, timeout_seconds=86400):
        '''Upload an image from filesystem to Openstack Glance.'''

        conn = self._get_connection()
        image = conn.image.create_image(
            name=name,
            filename=path,
            disk_format='vmdk',
            container_format='bare',
            visibility='community',
            timeout=timeout_seconds,
            **meta,
        )
        return image['id']

    def upload_image_from_url(self, name: str, url :str, meta: dict, timeout_seconds=86400):
        '''Import an image from web url to Openstack Glance.'''

        conn = self._get_connection()
        image = conn.image.create_image(
            name=name,
            disk_format='vmdk',
            container_format='bare',
            visibility='community',
            timeout=timeout_seconds,
            **meta,
        )
        conn.image.import_image(image, method="web-download", uri=url)
        return image['id']

    def wait_image_ready(self, image_id: str, wait_interval_seconds=10, timeout=3600):
        '''Wait until an image get in ready state.'''

        conn = self._get_connection()
        start_time = datetime.now()
        while True:
            if (datetime.now()-start_time).total_seconds() > timeout:
                raise RuntimeError('Timeout for waiting image to get ready reached.')
            image = conn.image.get_image(image_id)
            if image['status'] == 'queued' or image['status'] == 'saving' or image['status'] == 'importing':
                sleep(wait_interval_seconds)
                continue
            if image['status'] == 'active':
                return
            raise RuntimeError(f"image upload to Glance failed due to image status {image['status']}")


def upload_and_publish_image(
    s3_client,
    cicd_cfg: glci.model.CicdCfg,
    release: glci.model.OnlineReleaseManifest,
) -> glci.model.OnlineReleaseManifest:
    """Import an image from S3 into OpenStack Glance."""

    image_name = f"gardenlinux-{release.version}"
    image_meta = {
        'architecture': release.architecture.name,
        'properties': cicd_cfg.publish.openstack.properties,
    }

    s3_image_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': release.s3_bucket, 'Key': release.s3_key},
    )

    uploader = OpenstackImageUploader(cicd_cfg.publish.openstack.openrc)
    image_id = uploader.upload_image_from_url(image_name, s3_image_url, image_meta)
    uploader.wait_image_ready(image_id)

    published_image = glci.model.OpenstackPublishedImage(
        region_name=cicd_cfg.publish.openstack.openrc.region,
        image_id=image_id,
        image_name=image_name,
    )
    return dataclasses.replace(release, published_image_metadata=published_image)
