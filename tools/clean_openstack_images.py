#!/usr/bin/env python3

import argparse
import openstack
import dataclasses
import os


@dataclasses.dataclass
class OpenStackRC:
    project_name: str
    region: str
    auth_url: str
    project_domain: str
    user_domain: str
    username: str
    password: str

    def is_complete(self) -> bool:
        def non_empty(s: str) -> bool:
            if s == None or len(s) == 0:
                return False
            return True

        return (
            non_empty(self.project_name)
            and non_empty(self.region)
            and non_empty(self.auth_url)
            and non_empty(self.project_domain)
            and non_empty(self.user_domain)
            and non_empty(self.username)
            and non_empty(self.password)
        )


def setup_and_run_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--use-credential-profile",
        action="store_true",
        dest="use_cc_config",
        help="use a credential profile instead of using the OpenStack RC file",
    )
    parser.add_argument(
        "--credential-profile",
        type=str,
        default="gardenlinux",
        dest="credential_profile",
        help="the name of the credetial profile from which the credentials should be sourced",
    )
    parser.add_argument(
        "--region",
        type=str,
        help="only delete the image in the given region when using config profile",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        default=False,
        help="delete amis and associated snapshots",
    )
    parser.add_argument(
        "--visibility",
        type=str,
        default="community",
        help="the visibility of the images to look out for",
    )
    parser.add_argument(
        "--image-name",
        action="store_true",
        default=False,
        help="the name of the images to be removed across multiple regions (if given) - will also remove duplicates",
    )
    parser.add_argument(
        "image_id",
        type=str,
        help="the ID of the image to be removed (only for single region)",
    )

    args = parser.parse_args()
    return args


def get_openstack_rc(args) -> list[OpenStackRC]:
    if args.use_cc_config:
        import ctx

        cfg_factory = ctx.cfg_factory()
        cc_openstack = cfg_factory.ccee(args.credential_profile)
        os_credentials = cc_openstack.credentials()

        openstack_rcs = []
        for os_project in cc_openstack.projects():
            openstack_rcs.append(
                OpenStackRC(
                    project_name=os_project.name(),
                    region=os_project.region(),
                    auth_url=os_project.auth_url(),
                    project_domain=os_project.domain(),
                    user_domain=os_project.domain(),
                    username=os_credentials.username(),
                    password=os_credentials.passwd(),
                )
            )
        return openstack_rcs
    else:
        import os

        os_rc = OpenStackRC(
            project_name=os.getenv("OS_PROJECT_NAME"),
            region=os.getenv("OS_REGION_NAME"),
            auth_url=os.getenv("OS_AUTH_URL"),
            project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
            user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
            username=os.getenv("OS_USERNAME"),
            password=os.getenv("OS_PASSWORD"),
        )
        if os_rc.is_complete():
            return [os_rc]
        else:
            raise RuntimeError(f"no OpenStack credentials found")


def get_images_by_name(glance_proxy, name: str, visibility: str = "public"):
    images = []

    for i in glance_proxy.images(visibility=visibility):
        if i.name == name:
            images.append(i)

    return images


def get_image_by_id(glance_proxy, id: str):
    return [glance_proxy.find_image(name_or_id=id)]


def main():
    args = setup_and_run_argparser()

    openstack_rcs = get_openstack_rc(args)

    for orc in openstack_rcs:
        if args.region and args.region != orc.region:
            continue

        os_connection = openstack.connect(
            auth_url=orc.auth_url,
            project_name=orc.project_name,
            region_name=orc.region,
            user_domain_name=orc.user_domain,
            project_domain_name=orc.project_domain,
            username=orc.username,
            password=orc.password,
        )
        glance = os_connection.image

        if args.image_name:
            images = get_images_by_name(
                glance, name=args.image_id, visibility=args.visibility
            )
        else:
            images = get_image_by_id(
                glance, id=args.image_id
            )

        for i in images:
            if args.no_dry_run:
                print(
                    f" > Deleting image {i.name} with ID {i.id} in region {orc.region}"
                )
                glance.delete_image(i)
            else:
                print(
                    f" > Would delete image {i.name} with ID {i.id} in region {orc.region}"
                )


if __name__ == "__main__":
    main()
