
import subprocess
import logging
import json

logger = logging.getLogger(__name__)

class AzureWrapper:
    """Wrapper module to allow both, API as well as az tool usage"""

    def __init__(self, config):
        self.subscription = config["subscription"]
        self.resource_group = config["resource_group"]


# "--os-disk-delete-option", "Delete" "--nic-delete-option", "Delete",
    def create_vm(self, image, name, admin_username, nsg, ssh_key_name, size):
        cmd = [ "az", "vm", "create", 
                "--public-ip-sku", "Standard", 
                "--image", image, "--name", name, "--subscription", self.subscription, "--resource-group", self.resource_group, "--admin-username", admin_username, "--nsg", nsg, "--ssh-key-name", ssh_key_name, "--size", size]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to create vm %s" % result.stderr.decode('utf-8'))
        doc = json.loads(result.stdout)
        logger.info(json.dumps(doc, indent=4))
        return doc


    def get_vm(self, name):
        """
{
  "additionalCapabilities": null,
  "availabilitySet": null,
  "billingProfile": null,
  "diagnosticsProfile": null,
  "evictionPolicy": null,
  "extendedLocation": null,
  "extensionsTimeBudget": null,
  "hardwareProfile": {
    "vmSize": "Standard_B1s"
  },
  "host": null,
  "hostGroup": null,
  "id": "/subscriptions/00d2caa5-cd29-46f7-845a-2f8ee0360ef5/resourceGroups/garden-linux/providers/Microsoft.Compute/virtualMachines/integration-test",
  "identity": null,
  "instanceView": {
    "assignedHost": null,
    "bootDiagnostics": null,
    "computerName": "integration-test",
    "disks": [
      {
        "encryptionSettings": null,
        "name": "integration-test_disk1_325f9ec9e04e48d3b0458bba0e051076",
        "statuses": [
          {
            "code": "ProvisioningState/succeeded",
            "displayStatus": "Provisioning succeeded",
            "level": "Info",
            "message": null,
            "time": "2021-08-30T16:20:42.063646+00:00"
          }
        ]
      }
    ],
    "extensions": null,
    "hyperVGeneration": "V1",
    "maintenanceRedeployStatus": null,
    "osName": "debian",
    "osVersion": "testing/unstable",
    "patchStatus": null,
    "platformFaultDomain": null,
    "platformUpdateDomain": null,
    "rdpThumbPrint": null,
    "statuses": [
      {
        "code": "ProvisioningState/succeeded",
        "displayStatus": "Provisioning succeeded",
        "level": "Info",
        "message": null,
        "time": "2021-08-30T16:21:40.485886+00:00"
      },
      {
        "code": "PowerState/running",
        "displayStatus": "VM running",
        "level": "Info",
        "message": null,
        "time": null
      }
    ],
    "vmAgent": {
      "extensionHandlers": [],
      "statuses": [
        {
          "code": "ProvisioningState/succeeded",
          "displayStatus": "Ready",
          "level": "Info",
          "message": "Guest Agent is running",
          "time": "2021-08-30T16:26:49+00:00"
        }
      ],
      "vmAgentVersion": "2.2.47"
    },
    "vmHealth": null
  },
  "licenseType": null,
  "location": "westeurope",
  "name": "integration-test",
  "networkProfile": {
    "networkInterfaces": [
      {
        "id": "/subscriptions/00d2caa5-cd29-46f7-845a-2f8ee0360ef5/resourceGroups/garden-linux/providers/Microsoft.Network/networkInterfaces/integration-testVMNic",
        "primary": null,
        "resourceGroup": "garden-linux"
      }
    ]
  },
  "osProfile": {
    "adminPassword": null,
    "adminUsername": "azureuser",
    "allowExtensionOperations": true,
    "computerName": "integration-test",
    "customData": null,
    "linuxConfiguration": {
      "disablePasswordAuthentication": true,
      "patchSettings": {
        "patchMode": "ImageDefault"
      },
      "provisionVmAgent": true,
      "ssh": {
        "publicKeys": [
          {
            "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDGjTwl7kZlTW+sj1f2EALGxJUibvnIILs5Ol+pxx+06h05lZp+eyiiOTQYVnvoH6N6D1Ss53G4+dxEmEFACAKs6+Lqzi+1mE0+HGzZsjCMLfigbSIDlI0PJLt313qkk6v4PXSe2oYr6gt9LR/f34i8/gPXgr/UYRTjOMjozuRLVhEe6hu6zb5mYmquAciQ2jig+70Pb/7QWDy3uwX17lH8czHqryODwjOH1wCl95bg1d+zlw6IR8T17RlAg1FOyqtrcZlGUfeupMJEm9ShGs5GHVu0qtqKIF8eAzOuRjbDEfq9IIU1iJAAml2R/aZdbyZyMsKx1rwFT9eN7S1JBzu/",
            "path": "/home/azureuser/.ssh/authorized_keys"
          }
        ]
      }
    },
    "requireGuestProvisionSignal": true,
    "secrets": [],
    "windowsConfiguration": null
  },
  "plan": null,
  "platformFaultDomain": null,
  "priority": null,
  "provisioningState": "Succeeded",
  "proximityPlacementGroup": null,
  "resourceGroup": "garden-linux",
  "resources": null,
  "securityProfile": null,
  "storageProfile": {
    "dataDisks": [],
    "imageReference": {
      "exactVersion": null,
      "id": "/subscriptions/00d2caa5-cd29-46f7-845a-2f8ee0360ef5/resourceGroups/garden-linux/providers/Microsoft.Compute/images/garden-linux-318.6.0",
      "offer": null,
      "publisher": null,
      "resourceGroup": "garden-linux",
      "sku": null,
      "version": null
    },
    "osDisk": {
      "caching": "ReadWrite",
      "createOption": "FromImage",
      "diffDiskSettings": null,
      "diskSizeGb": 4,
      "encryptionSettings": null,
      "image": null,
      "managedDisk": {
        "diskEncryptionSet": null,
        "id": "/subscriptions/00d2caa5-cd29-46f7-845a-2f8ee0360ef5/resourceGroups/garden-linux/providers/Microsoft.Compute/disks/integration-test_disk1_325f9ec9e04e48d3b0458bba0e051076",
        "resourceGroup": "garden-linux",
        "storageAccountType": "Standard_LRS"
      },
      "name": "integration-test_disk1_325f9ec9e04e48d3b0458bba0e051076",
      "osType": "Linux",
      "vhd": null,
      "writeAcceleratorEnabled": null
    }
  },
  "tags": {},
  "type": "Microsoft.Compute/virtualMachines",
  "virtualMachineScaleSet": null,
  "vmId": "21d82b34-a35a-482f-841d-7fa8b17e4c8c",
  "zones": null
}
"""

        cmd = [
                 "az",
                 "vm",
                 "get-instance-view",
                 "--resource-group",
                 self.resource_group,
                 "--subscription", 
                 self.subscription,
                 "--name",
                 name]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return None
        return json.loads(result.stdout)


    def terminate_vm(self, id):
        cmd = [ "az", "vm", "delete", 
                "--subscription", self.subscription, "--resource-group", self.resource_group, "--yes", "--ids", id]        
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return Exception("Unable to terminate vm %s" % result.stderr.decode("utf-8"))


    def delete_disk(self, id):
        cmd = [ "az", "disk", "delete", "--yes", "--ids", id]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            logger.error("Unable to delete disk " + result.stderr.decode("utf-8"))

    def delete_vm_nic(self, id):
        cmd = [ "az", "network", "nic", "delete", "--ids", id]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            logger.error("Unable to delete network nic " + result.stderr.decode("utf-8"))


    def get_nsg(self, name):
        cmd = ["az", "network", "nsg", "show", "--subscription", self.subscription, "--name", name, "--resource-group", self.resource_group]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return None
        return json.loads(result.stdout)

    def delete_nsg(self, name):
        cmd = ["az", "network", "nsg", "delete", "--subscription", self.subscription, "--name", name, "--resource-group", self.resource_group]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return Exception("Unable to delete nsg %s" % result.stderr.decode("utf-8"))


    def create_nsg(self, name):        
        cmd = ["az", "network", "nsg", "create", "--name", name, "--subscription", self.subscription, "--resource-group", self.resource_group]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to create network security group: %s" + result.stderr.decode('utf-8'))

        cmd = ["az", "network", "nsg", "rule", "create", "--name", "ssh", "--nsg-name", name, 
               "--priority", "300", 
               "--destination-port-ranges", "22",
               "--access", "Allow", "--protocol", "Tcp", "--source-address-prefixes", "0.0.0.0/1",  "128.0.0.0/1", "--subscription", self.subscription, "--resource-group", self.resource_group]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to add rule to nsg %s" % result.stderr.decode("utf-8"))


    def get_ssh_key(self, ssh_keyname):
        cmd = [
            "az", "sshkey", "show", "--subscription", self.subscription, "--resource-group", self.resource_group, "--name", ssh_keyname
        ]
        if result.returncode != 0:
            return None
        else:
            return json.loads(result.stdout)


    def upload_ssh_key(self, ssh_keypath, ssh_keyname):
        k = paramiko.RSAKey.from_private_key_file(os.path.abspath(ssh_keypath))
        pub = k.get_name() + " " + k.get_base64()
        logger.info("Uploading key %s" % ssh_keyname)
        cmd = [
            os.path.join(self.repo_root, "az"), "sshkey", "create", "--subscription", self.subscription, "--resource-group", self.resource_group, "--public-key", pub, "--name", ssh_keyname
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception("Error uploading key: %s" % (result.stderr.decode("utf-8")))


    def delete_ssh_key(self, ssh_keyname):
        raise Exception("not yet implemented")
