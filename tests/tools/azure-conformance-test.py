#!/usr/bin/env python3
#
# See https://learn.microsoft.com/en-us/azure/marketplace/azure-vm-image-test#run-validations for what this is all about
#
# Requires a running VM on Azure that has a user and an SSH public-key for that user in it.

import requests
import dataclasses
import argparse
import pprint
import json


@dataclasses.dataclass
class AzureVmToBeTested:
    dns_name: str
    os: str
    ssh_port: int

@dataclasses.dataclass
class AzureVmCredentials:
    username: str
    password: str

@dataclasses.dataclass
class AzureServicePrincipal:
    tenant_id: str
    client_id: str
    client_secret: str
    subscription_id: str


def get_az_service_principal_from_spn_config(service_principal_cfg_name: str) -> AzureServicePrincipal:
    # late import as we only need it if we want to use the cfg_factory
    # requires gardener ci-cd utils: pip install gardener-cicd-base
    import ci.util

    cfg_factory = ci.util.ctx().cfg_factory()
    azure_principal = cfg_factory.azure_service_principal(
        cfg_name=service_principal_cfg_name,
    )

    azure_principal_serialized = AzureServicePrincipal(
        tenant_id=azure_principal.tenant_id(),
        client_id=azure_principal.client_id(),
        client_secret=azure_principal.client_secret(),
        subscription_id=azure_principal.subscription_id(),
    )

    return azure_principal_serialized


def get_az_bearer_token(service_principal: AzureServicePrincipal) -> str:
    url = f"https://login.microsoftonline.com/{service_principal.tenant_id}/oauth2/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    data = {
        "grant_type": "client_credentials",
        "client_id": service_principal.client_id,
        "client_secret": service_principal.client_secret,
        "resource": "https://management.core.windows.net",        
    }

    response = requests.post(url=url, data=data, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"did not obtain valid bearer token ({response.status_code=})")
    
    result = response.json()
    return result.get('access_token')


def invoke_vm_test(vm_to_be_tested: AzureVmToBeTested, vm_credentials: AzureVmCredentials, service_pricipal: AzureServicePrincipal, bearer_token: str):
    url = "https://isvapp.azurewebsites.net/selftest-vm"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {bearer_token}',
    }

    data = {
        "DNSName": vm_to_be_tested.dns_name,
        "UserName": vm_credentials.username,
        "Password": vm_credentials.password,
        "OS": vm_to_be_tested.os,
        "PortNo": str(vm_to_be_tested.ssh_port),
        "CompanyName": "SAP SE",
        "AppId": service_pricipal.client_id,
        "TenantId": service_pricipal.tenant_id,
    }

    response = requests.post(url=url, headers=headers, json=data)
    if response.status_code != 200:
        raise RuntimeError(f"did not obtain valid response ({response.status_code=}): {response.content=}")
    
    return response.json()


def read_ssh_private_key(ssh_private_key_path: str) -> str:
    private_key = ""
    with open(ssh_private_key_path, "r") as f:
        private_key = f.read()
    return private_key


def setup_and_run_argparser():
    parser = argparse.ArgumentParser(description='Run Azure Marketplace conformance agains a running VM')
    parser.add_argument('dns_name', metavar='dns_name', type=str, nargs=1, help='the DNS name/IP address to the VM')
    parser.add_argument('-u', '--user', dest="user", type=str, default='azureuser', help='username to log in to the VM')
    parser.add_argument('-p', '--password', dest="password", type=str, help='password to log in to the VM')
    parser.add_argument('-s', '--ssh-private-keyfile', dest='ssh_privkey', type=str, help='path to SSH private key file to log in')

    # this is used for obtaining Azure Service Principal information from Gardener/Gardenlinux CI/CD infrastructure
    parser.add_argument('--spn-config-name', dest="sp_config_name", type=str, help='name of the service principal configuration')

    # these are for providing Azure Service Principal information manually
    parser.add_argument('--client-id', dest="az_client_id", type=str, help='Azure Client ID')
    parser.add_argument('--client-secret', dest="az_client_secret", type=str, help='Azure Client Secret')
    parser.add_argument('--tenant-id', dest="az_tenant_id", type=str, help='Azure Tenant ID')
    parser.add_argument('--subscription-id', dest="az_subscription_id", type=str, help='Azure Subscription ID')

    args = parser.parse_args()

    if not args.dns_name or len(args.dns_name) != 1:
        raise RuntimeError("must supply name of VM to test")
    if not args.user:
        raise RuntimeError("must supply username to log in to VM")
    if not args.password and not args.ssh_privkey:
        raise RuntimeError("must supply either password or SSH private key to log in to VM")
    
    if not args.sp_config_name or len(args.sp_config_name) == 0:
        az_sp_config_count = 0
        if args.az_client_id:
            az_sp_config_count = az_sp_config_count + 1
        if args.az_client_secret:
            az_sp_config_count = az_sp_config_count + 1
        if args.az_tenant_id:
            az_sp_config_count = az_sp_config_count + 1
        if args.az_subscription_id:
            az_sp_config_count = az_sp_config_count + 1
        if az_sp_config_count != 4:
            raise RuntimeError("must either supply --spn-config-name or all four of --client-id, --client-secret, --tenant-id, --subscription-id")

    return args


if __name__ == "__main__":
    args = setup_and_run_argparser()

    service_principal = None

    if args.sp_config_name:
        service_principal = get_az_service_principal_from_spn_config(args.sp_config_name)
    else:
        service_principal = AzureServicePrincipal(
            tenant_id=args.az_tenant_id,
            client_id=args.az_client_id,
            client_secret=args.az_client_secret,
            subscription_id=args.az_subscription_id,
        )
    
    bearer_token = get_az_bearer_token(service_principal)

    password = ""
    if args.ssh_privkey:
        password = read_ssh_private_key(args.ssh_privkey)
    else:
        password = args.password

    vm_to_test = AzureVmToBeTested(
        dns_name=args.dns_name[0],
        os="Linux",
        ssh_port=22,
    )

    credentials = AzureVmCredentials(
        username=args.user,
        password=password,
    )

    print(f"Invoking Azure VM Self-Test (https://isvapp.azurewebsites.net/selftest-vm) on {vm_to_test.dns_name}...")

    az_test_response = invoke_vm_test(
        vm_to_be_tested=vm_to_test,
        vm_credentials=credentials,
        service_pricipal=service_principal,
        bearer_token=bearer_token,
    )

    test_results = json.loads(az_test_response['Response'])

    print("Azure VM Self-Test")
    print("--------------------------------")
    print(f"Certification Category : {test_results.get('AppCertificationCategory', 'undefined')}")
    print(f"Created Date           : {test_results.get('CreatedDate', 'undefined')}")
    print(f"Provider ID            : {test_results.get('ProviderID', 'undefined')}")
    print(f"API Version            : {test_results.get('APIVersion', 'undefined')}")
    print("")
    print("General")
    print("--------------------------------")
    print(f"OS Distro  : {test_results.get('OSDistro', 'undefined')}")
    print(f"OS Name    : {test_results.get('OSName', 'undefined')}")
    print(f"OS Version : {test_results.get('OSVersion', 'undefined')}")
    print("")
    print("Test case results")
    print("--------------------------------")

    for result in sorted(test_results.get('Tests'), key=lambda id: id['TestID']):
        print(f"Test name (ID)   : {result.get('TestCaseName')} ({result.get('TestID')})")
        print(f"  Description    : {result.get('Description')}")
        print(f"  Required Value : {result.get('RequiredValue', 'undefined')}")
        print(f"  Actual Value   : {result.get('ActualValue', 'undefined')}")
        print(f"  Result         : {result.get('Result')}")
        print("")
