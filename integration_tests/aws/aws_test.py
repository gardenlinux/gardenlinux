
import boto3
import ccc.aws
import pytest


def test_aws_describe_instances(ec2_client):
    '''dummy test demonstrates how to interact with EC2'''
    instances = ec2_client.describe_instances()
    assert(instances)
    assert(type(instances) is dict)
    assert(len(instances) > 0)
