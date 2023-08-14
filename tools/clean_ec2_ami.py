#!/usr/bin/env python3

import argparse
import boto3
import functools
import sys


def response_ok(response: dict):
    resp_meta = response["ResponseMetadata"]
    if (status_code := resp_meta["HTTPStatusCode"]) == 200:
        return response

    raise RuntimeError(f'rq {resp_meta["RequestId"]=} failed {status_code=}')


def delete_snapshot(client, snapshot_id: str):
    response_ok(
        client.delete_snapshot(
            SnapshotId=snapshot_id,
        )
    )


def find_snapshots(client, ami_id: str):
    snapshots = []

    resp = response_ok(
        client.describe_images(
            Owners=["self"], Filters=[{"Name": "image-id", "Values": [ami_id]}]
        )
    )

    if len(resp["Images"]) > 0:
        image = resp["Images"][0]

        for bdm in image.get("BlockDeviceMappings"):
            snapshots.append(bdm["Ebs"]["SnapshotId"])

    return snapshots


def get_resource_tags(client, resource_id: str, key: str = None):
    resp = response_ok(
        client.describe_tags(
            Filters=[
                {
                    "Name": "resource-id",
                    "Values": [resource_id],
                },
            ],
        )
    )

    if key == None:
        return resp.get("Tags")
    else:
        for t in resp.get("Tags"):
            if t["Key"] == key:
                return t["Value"]
        return None


def find_ami_by_name_across_regions(client, ami_name: str, mk_session: callable):
    regions = response_ok(client.describe_regions()).get("Regions")

    amis = {}

    for r in regions:
        region = r.get("RegionName")
        session_r = mk_session(region_name=region)
        ec2_r = session_r.client("ec2")
        image_ids = []

        resp = response_ok(ec2_r.describe_images(Owners=["self"]))
        for i in resp.get("Images"):
            if i["Name"] == ami_name:
                image_ids.append(i["ImageId"])

        amis[region] = image_ids

    return amis


def find_ami_copies(session, mk_session: callable, source_ami_id: str):
    ec2 = session.client("ec2")
    regions = response_ok(ec2.describe_regions()).get("Regions")

    ami_copies = {}

    for r in regions:
        region = r.get("RegionName")
        session_r = mk_session(region_name=region)
        ec2_r = session_r.client("ec2")

        resp = response_ok(ec2_r.describe_images(Owners=["self"]))
        for i in resp.get("Images"):
            id = i["ImageId"]
            if src_ami := get_resource_tags(ec2_r, id, "source_ami") != None:
                ami_copies[region] = id
                break

    return ami_copies


def un_public_ami(ec2_client, ami_id: str, no_dry_run: bool = False):
    if no_dry_run:
        print(f" > Setting image sharing permissions for ami with {ami_id=} to private")
        response_ok(
            ec2_client.modify_image_attribute(
                ImageId=ami_id,
                LaunchPermission={
                    "Remove": [
                        {
                            "Group": "all",
                        },
                    ],
                },
            )
        )
    else:
        print(
            f" > Would set image sharing permissions for ami with {ami_id=} to private"
        )


def delete_ami_with_snapshot(ec2_client, ami_id: str, no_dry_run: bool = False):
    snapshots = find_snapshots(ec2_client, ami_id=ami_id)

    if no_dry_run:
        print(f" > Deleting AMI {ami_id=}")
        response_ok(
            ec2_client.deregister_image(
                ImageId=ami_id,
            )
        )

        for snapshot in snapshots:
            print(f"   - deleting corresponding {snapshot=}")
            response_ok(ec2_client.delete_snapshot(SnapshotId=snapshot))
    else:
        print(f" > Would delete AMI {ami_id=}")
        for snapshot in snapshots:
            print(f"   - would delete corresponding {snapshot=}")


def setup_and_run_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--profile_name",
        type=str,
        default=None,
        help="the name of the AWS profie to use (equivalent to AWS_PROFILE_NAME environment variable",
    )
    parser.add_argument("--region", type=str, help="AWS region", required=True)
    parser.add_argument(
        "--single-region",
        action="store_true",
        default=False,
        help="only delete the AMI in the given region",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        default=False,
        help="delete amis and associated snapshots",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        default=False,
        help="delete amis and associated snapshots",
    )
    parser.add_argument(
        "--un-publicise",
        action="store_true",
        default=False,
        help="set amis from public to private",
    )
    parser.add_argument(
        "ami_id",
        type=str,
        help="this is the ID of the first AMI that was created (and which might have been copied into other regions)",
    )
    parser.add_argument(
        "--ami-name",
        action="store_true",
        default=False,
        help="this is the name of an AMI to be deleted (should be the same in all regions)",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = setup_and_run_argparser()
    session = boto3.Session(profile_name=args.profile_name, region_name=args.region)
    client = session.client("ec2")
    mk_session = functools.partial(boto3.Session, profile_name=args.profile_name)

    action_func = None
    if args.delete is True:
        action_func = functools.partial(
            delete_ami_with_snapshot, no_dry_run=args.no_dry_run
        )
    elif args.un_publicise is True:
        action_func = functools.partial(un_public_ami, no_dry_run=args.no_dry_run)

    if args.single_region:
        action_func(ec2_client=client, ami_id=args.ami_id)
        sys.exit(0)

    # ami_copies = find_ami_copies(session=session, mk_session=mk_session, source_ami_id=args.ami_id)

    if args.ami_name:
        amis = find_ami_by_name_across_regions(
            client, ami_name=args.ami_id, mk_session=mk_session
        )

    for region in amis:
        session_r = mk_session(region_name=region)
        ec2_r = session_r.client("ec2")

        for ami in amis[region]:
            action_func(ec2_client=ec2_r, ami_id=ami)
