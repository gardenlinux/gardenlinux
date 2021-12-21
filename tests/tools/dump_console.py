#!/usr/bin/env python3

import boto3
import click
import base64
import os



@click.command()
@click.option('--instanceid', required=True, help='InstanceID from AWS instance')
@click.option('--output', help='Append output to the file provided. Default is <instanceID>.dump')
def dump_comsole(instanceid, output):
    """If the instanceid exists the serial console is dumped to file """
    session = boto3.Session()
    client = session.client("ec2")

    if not output:
        output = f"{instanceid}.dump"

    response = client.get_console_output(InstanceId = f"{instanceid}")

    print(response)
    
    if not os.path.exists(output):
        with open(output, 'w'): pass

    with open(output, 'w') as writer:
        writer.write(response['Output'])

if __name__ == '__main__':
    dump_comsole()




