#!/usr/bin/env python3

import argparse
import re
import os

import google.cloud.compute as compute
import google.cloud.storage as storage


parser = argparse.ArgumentParser(description = 'Cleanup integration test resources in GCP')
parser.add_argument('-p', '--project', metavar='project_id', required=False, dest='project', default='sap-cp-k8s-gdnlinux-gcp-test',
                    help='Default value is "sap-cp-k8s-gdnlinux-gcp-test"')
parser.add_argument('-r', '--region', metavar='region', required=False, dest='region', default='europe-west1', 
                    help='Default value is "europe-west1"')
parser.add_argument('-z', '--zone', metavar='zone', required=False, dest='zone', default='europe-west1-d',
                    help='Default value is "europe-west1-d"')
args = parser.parse_args()

storage_client = storage.Client(project=args.project)
image_client = compute.ImagesClient()
subnet_client = compute.SubnetworksClient()
firewall_client = compute.FirewallsClient()
network_client = compute.NetworksClient()
instance_client = compute.InstancesClient()


def wait_for_operation(operation, name):
    print(f"Waiting for deletion of resource {name} to complete...")
    result = operation.result()
    print(f"    {name} deleted.")


def get_buckets():
    bucket_list = list(storage_client.list_buckets())
    return bucket_list


def delete_bucket(name):
    bucket = storage_client.bucket(bucket_name=name)
    print(f"Deleting bucket {name}...")
    bucket.delete(force=True)
    print(f"    {name} deleted.")


def get_images(project):
    image_list = image_client.list(project=project).items
    return image_list


def delete_image(project, name):
    operation = image_client.delete(project=project, image=name)
    wait_for_operation(operation, name)


def get_subnets(project, region):
    subnet_list = subnet_client.list(project=project, region=region).items
    return subnet_list


def delete_subnet(project, region, name):
    operation = subnet_client.delete(project=project, region=region, subnetwork=name)
    wait_for_operation(operation, name)


def get_firewalls(project):
    firewall_list = firewall_client.list(project=project).items
    return firewall_list


def delete_firewall(project, name):
    operation = firewall_client.delete(project=project, firewall=name)
    wait_for_operation(operation, name)


def get_networks(project):
    network_list = network_client.list(project=project).items
    return network_list


def delete_network(project, name):
    operation = network_client.delete(project=project, network=name)
    wait_for_operation(operation, name)


def get_instances(project, zone):
    instance_list = instance_client.list(project=project, zone=zone).items
    return instance_list


def delete_instance(project, zone, name):
    operation = instance_client.delete(project=project, zone=zone, instance=name)
    wait_for_operation(operation, name)


def add_to_inventory(inventory_dict, key, value):
    try:
        if type(inventory_dict[key]) is dict:
            inventory[key].update(value)
    except KeyError:
        inventory_dict[key] = value
    return inventory_dict


def sanity_check(inventory_dict, dependencies):
    for dependency in dependencies:
        if dependency in inventory_dict:
            return False
    return True


while True:

    buckets = get_buckets()
    images = get_images(args.project)
    subnets = get_subnets(args.project, args.region)
    firewalls = get_firewalls(args.project)
    networks = get_networks(args.project)
    instances = get_instances(args.project, args.zone)

    # build inventory, key is the test name, value is a dict with the resources of the test
    inventory = {}

    for instance in instances:
        inventory = add_to_inventory(inventory, instance.labels['test-name'], {"instance": instance.name})

    for bucket in buckets:
        inventory = add_to_inventory(inventory, bucket.labels['test-name'], {"bucket": bucket.name})

    for image in images:
        inventory = add_to_inventory(inventory, image.labels['test-name'], {"image": image.name})

    for subnet in subnets:
        inventory = add_to_inventory(inventory, re.sub(r"vpc-", "", subnet.name), {"subnet": subnet.name})

    for firewall in firewalls:
        inventory = add_to_inventory(inventory, re.sub(r"http.*vpc-", "", firewall.network) , {"firewall": firewall.name})

    for network in networks:
        inventory = add_to_inventory(inventory, re.sub(r"vpc-", "", network.name), {"network": network.name})

    inventory_key_list = list(inventory)

    for i in range(len(inventory_key_list)):
        print(f"{i}: {inventory_key_list[i]}")
        for key,value in inventory[inventory_key_list[i]].items():
            print(f"       {key}: {value}")
        print("")

    pick = input("Choose the test resources to delete (digit, any other key quits): ")
    try:
        pick = int(pick)

        if not (pick >= 0 and pick < len(inventory_key_list)):
            os._exit(os.EX_DATAERR)

        test_environment = inventory_key_list[pick]

        while True:
            test_inventory_key_list = list(inventory[test_environment])
            if len(test_inventory_key_list) == 0:
                break

            # output the resources of the chosen test, offer option to delete one resource or all at once
            print("")
            for i in range(len(test_inventory_key_list)):
                print(f"{i}: {test_inventory_key_list[i]}: {inventory[test_environment][test_inventory_key_list[i]]}")
            print("")
            delete_pick = input("Which resource should be delete (digit), type 'A' for all, any other key for back: ")
            if (delete_pick == 'A'):
                pass
            elif delete_pick.strip().isdigit():
                delete_pick = int(delete_pick)
                if (delete_pick >= 0 and delete_pick < len(test_inventory_key_list)):
                    pass
                else:
                    break
            else:
                break

            # check if resource is deletable, delete resource if possible
            for i in range(len(test_inventory_key_list)):
                if delete_pick == i or delete_pick == 'A':
                    if test_inventory_key_list[i] == 'instance':
                        print("Deleting instance...")
                        delete_instance(args.project, args.zone, inventory[test_environment]['instance'])
                        del inventory[test_environment]['instance']
                    if test_inventory_key_list[i] == 'subnet':
                        print("Deleting subnet...")
                        if sanity_check(inventory[test_environment], ['instance']):
                            delete_subnet(args.project, args.region, inventory[test_environment]['subnet'])
                            del inventory[test_environment]['subnet']
                        else:
                            print(f"subnet {inventory[test_environment]['subnet']} is in use by an instance")
                            continue
                    if test_inventory_key_list[i] == 'firewall':
                        print("Deleting firewall...")
                        delete_firewall(args.project, inventory[test_environment]['firewall'])
                        del inventory[test_environment]['firewall']
                    if test_inventory_key_list[i] == 'network':
                        print("Deleting network...")
                        if sanity_check(inventory[test_environment], ['instance', 'subnet', 'firewall']):
                            delete_network(args.project, inventory[test_environment]['network'])
                            del inventory[test_environment]['network']
                        else:
                            print(f"network {inventory[test_environment]['network']} is in use by an instance, subnet or firewall")
                            continue
                    if test_inventory_key_list[i] == 'image':
                        print("Deleting image...")
                        delete_image(args.project, inventory[test_environment]['image'])
                        del inventory[test_environment]['image']
                    if test_inventory_key_list[i] == 'bucket':
                        print("Deleting bucket...")
                        delete_bucket(inventory[test_environment]['bucket'])
                        del inventory[test_environment]['bucket']
            print("")

    except ValueError:
        os._exit(os.EX_OK)