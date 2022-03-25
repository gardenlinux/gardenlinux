#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError

def clean_keypairs(client, force: bool = False):
    keypairs = client.describe_key_pairs(
        Filters=[
            {'Name': 'tag:component', 'Values': ['gardenlinux']},
            {'Name': 'tag:test-type', 'Values': ['integration-test']}
        ]
    )

    if len(keypairs['KeyPairs']) == 0:
        print("No SSH Keypairs originating from tests found.")
        return

    for key in keypairs['KeyPairs']:
        print(f"Name: {key['KeyName']}\tID: {key['KeyPairId']}")
        print(f"Fingerprint: {key['KeyFingerprint']}")
        print("Tags:")
        for t in key['Tags']:
            print(f"\t{t['Key']}: {t['Value']}")
        
        if not force:
            delete = input(f"\nDelete this key (y/N)? ")
        if delete == "y" or force:
            client.delete_key_pair(KeyPairId = key['KeyPairId'])


def clean_images(client, force: bool = False):
    images = client.describe_images(
        Filters=[
            {'Name': 'tag:component', 'Values': ['gardenlinux']},
            {'Name': 'tag:test-type', 'Values': ['integration-test']}
        ]
    )

    if len(images['Images']) == 0:
        print("No images/amis originating from tests found.")
        return

    for img in images['Images']:
        print(f"Name: {img['Name']}\tID: {img['ImageId']}")
        print(f"Created On: {img['CreationDate']}")
        print(f"Public: {img['Public']}")
        print("Tags:")
        for t in img['Tags']:
            print(f"\t{t['Key']}: {t['Value']}")
        
        if not force:
            delete = input(f"\nDeregister this image (y/N)? ")
        if delete == "y" or force:
            client.deregister_image(ImageId = img['ImageId'])


def clean_security_groups(client, force: bool = False):
    secgroups = client.describe_security_groups(
        Filters=[
            {'Name': 'tag:component', 'Values': ['gardenlinux']},
            {'Name': 'tag:test-type', 'Values': ['integration-test']}
        ]
    )

    if len(secgroups['SecurityGroups']) == 0:
        print("No security groups originating from tests found.")
        return

    for sg in secgroups['SecurityGroups']:
        print(f"Name: {sg['GroupName']}\tID: {sg['GroupId']}")
        print(f"VPC: {sg['VpcId']}")
        print("Permissions:")
        for perm in sg['IpPermissions']:
            print(f"\tPortrange: {perm['FromPort']} - {perm['ToPort']}")
            print(f"\tIP-Ranges:")
            for range in perm['IpRanges']:
                print(f"\t\t{range['CidrIp']}")
        print("Tags:")
        for t in sg['Tags']:
            print(f"\t{t['Key']}: {t['Value']}")
        
        if not force:
            delete = input(f"\nDelete this security group (y/N)? ")
        if delete == "y" or force:
            client.delete_security_group(GroupId = sg['GroupId'])


def clean_snapshot(client, force: bool = False):
    snapshots = client.describe_snapshots(
        Filters=[
            {'Name': 'tag:component', 'Values': ['gardenlinux']},
            {'Name': 'tag:test-type', 'Values': ['integration-test']}
        ]
    )

    if len(snapshots['Snapshots']) == 0:
        print("No snapshots originating from tests found.")
        return

    for snap in snapshots['Snapshots']:
        print(f"ID: {snap['SnapshotId']}")
        print("Tags:")
        for t in snap['Tags']:
            print(f"\t{t['Key']}: {t['Value']}")
        
        if not force:
            delete = input(f"\nDelete this snapshot (y/N)? ")
        if delete == "y" or force:
            client.delete_snapshot(SnapshotId = snap['SnapshotId'])


def clean_instances(client, force: bool = False):
    instances = client.describe_instances(
        Filters=[
            {'Name': 'tag:component', 'Values': ['gardenlinux']},
            {'Name': 'tag:test-type', 'Values': ['integration-test']}
        ]
    )

    instance_count = 0

    for r in instances['Reservations']:
        instance_count += len(r['Instances'])
        for i in r['Instances']:
            if i['State']['Code'] == 48: # instance terminated
                continue
            print(f"ID: {i['InstanceId']}\t\tUsed AMI: {i['ImageId']}")
            print(f"Type: {i['InstanceType']}")
            print(f"IP address: {i['PrivateIpAddress']}")
            print("Tags:")
            for t in i['Tags']:
                print(f"\t{t['Key']}: {t['Value']}")
            
            if not force:
                delete = input(f"\nTerminate this instance (y/N)? ")
            if delete == "y" or force:
                client.terminate_instances(InstanceIds = [i['InstanceId']])
                waiter = client.get_waiter('instance_terminated')
                print("Waiting for instance to terminate...")
                waiter.wait(InstanceIds=[i['InstanceId']])

    if instance_count == 0:
        print("No instances originating from tests found.")


def clean_buckets(client, force: bool = False):
    bucket_count = 0
    buckets = client.list_buckets()
    for bckt in buckets['Buckets']:
        try:
            tags = {tt['Key']:tt['Value'] for tt in client.get_bucket_tagging(Bucket=bckt['Name'])['TagSet']}
        except ClientError:
            continue
        if 'component' in tags and tags['component'] == 'gardenlinux' and 'test-type' in tags and tags['test-type'] == 'integration-test':
            bucket_count += 1
            print(f"Bucket name: {bckt['Name']}")
            print("Tags:")
            for k in tags.keys():
                print(f"\t{k}: {tags[k]}")

            contents = client.list_objects(Bucket=bckt['Name'])
            if 'Contents' in contents and len(contents['Contents']) > 0:
                print("\n\tContents:")
                for c in contents['Contents']:
                    print(f"\t\tKey: {c['Key']}")
                    try:
                        ctags = {tt['Key']:tt['Value'] for tt in client.get_object_tagging(Bucket=bckt['Name'], Key=c['Key'])['TagSet']}
                        print("\t\tTags:")
                        for k in ctags.keys():
                            print(f"\t\t\t{k}: {ctags[k]}")
                    except ClientError:
                        pass
                    if not force:
                        delete = input(f"\n\tDelete this object (y/N)? ")
                    if delete == "y" or force:
                        client.delete_object(Bucket=bckt['Name'], Key=c['Key'])

            if not force:
                delete = input(f"\nDelete this bucket ({bckt['Name']}) (y/N)? ")
            if delete == "y" or force:
                client.delete_bucket(Bucket=bckt['Name'])

    if bucket_count == 0:
        print("No buckets originating from tests found.")


if __name__ == "__main__":
    session = boto3.Session()
    ec2_client = session.client("ec2")
    s3_client = session.client("s3")

    print(f"Instances:")
    clean_instances(ec2_client)
    print(f"\nSecurity Groups:")
    clean_security_groups(ec2_client)
    print(f"\nImages/AMIs:")
    clean_images(ec2_client)
    print(f"\nSnapshots:")
    clean_snapshot(ec2_client)
    print(f"\nSSH Keypairs:")
    clean_keypairs(ec2_client)
    print(f"\nS3 buckets:")
    clean_buckets(s3_client)
    