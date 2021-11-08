# Spin up a Dev VM

This folder contains a simple vagrant setup,
that spins up a VM with all build dependencies installed and gardenlinux sources synced 
to ```/code```directory within the VM.

You can adapt the VM parameters in the ```Vagrantfile```. The ```init.sh```
is executed when the VM is provisioned, and installs all debian packages
listed in ```deps.list```.

## Create VM

```
# Create and Start the VM
vagrant up

# Login to the VM
vagrant ssh

```





