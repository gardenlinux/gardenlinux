# Spin up a Dev VM

This folder contains a simple vagrant setup,
that spins up a VM with all dependencies installed to build garden linux.
You can adapt the VM parameters in the ```Vagrantfile```. The ```init.sh```
is executed when the VM is provisioned, and installs all debian packages
listed in ```deps.list```.


Just run ```vagrant up``` to start the VM, and ```vagrant ssh``` to login
into a shell of the VM.




