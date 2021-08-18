import boto3
import ccc.aws
import pytest


@pytest.fixture(scope="session")
def aws_session(aws_cfg) -> boto3.Session:
    '''
    get boto3 session to be used to further interact with AWS objects 
    '''
    return ccc.aws.session(aws_cfg.aws_cfg_name, aws_cfg.aws_region)

@pytest.fixture(scope="session")
def ec2_client(aws_session):
    '''
    get boto3 ec2 client instance to further interact with AWS EC2 instances 
    '''
    return aws_session.client('ec2')

