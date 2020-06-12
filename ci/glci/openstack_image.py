import os
import time
import argparse

from glci.model import OpenRC

from openstack import connect

class OpenstackImageUploader:
  '''OpenstackImageUploader is a client to upload images to Openstack Glance.'''

  def __init__(self, openrc: OpenRC):
      self.conn = connect(
          auth_url=openrc.auth_url,
          project_name=openrc.project_name,
          username=openrc.username,
          password=openrc.password,
          region_name=openrc.region,
          user_domain_name=openrc.domain,
          project_domain_name=openrc.domain,
      )

  def upload_image(self, name: str, path: str, meta: dict, timeout_seconds=86400):
      '''Upload an image from filesystem to Openstack Glance.'''

      image = self.conn.image.create_image(
          name=name,
          filename=path,
          disk_format='vmdk',
          container_format='bare',
          visibility='community',
          meta=meta,
          timeout=timeout_seconds,
      )
      return image['id']

  def wait_image_ready(self, image_id: str, wait_interval_seconds=10):
      '''Wait until an image get in ready state.'''

      while True:
          image = self.conn.image.get_image(image_id)
          if image['status'] == 'queued' or image['status'] == 'saving':
              time.sleep(wait_interval_seconds)
              continue
          if image['status'] == 'active':
              return
          RuntimeError(f"image upload to Glance failed due to image status {image['status']}")


def upload_image(image_name: str, image_path: str, build_number: str, openrc: OpenRC, architecture='x86_64'):
    uploader = OpenstackImageUploader(openrc)
    image_meta = {
        'architecture': architecture,
        'properties': {
            'buildnumber': build_number,
        },
    }
    image_id = uploader.upload_image(image_name, image_path, image_meta)
    uploader.wait_image_ready(image_id)
    return image_id


def main():
    openrc = OpenRC(
        os.environ['OS_AUTH_URL'],
        os.environ['OS_PROJECT_DOMAIN_NAME'],
        os.environ['OS_REGION_NAME'],
        os.environ['OS_PROJECT_NAME'],
        os.environ['OS_USERNAME'],
        os.environ['OS_PASSWORD'],
    )

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--name', type=str, help='name of the image', required=True)
    parser.add_argument('--path', type=str, help='path to image file', required=True)
    parser.add_argument('--buildnumber', type=str, help='buildnumber of the image', required=True)
    args = parser.parse_args()

    upload_image(args.name, args.path, args.build_number, openrc)

if __name__ == '__main__':
    main()
