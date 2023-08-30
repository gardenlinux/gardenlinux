A word of **WARNING**: Since OpenStack is an open environment, we can only provide a reference implementation at this point.

Our reference implementation goes by the name _CC EE_ and uses OpenStack with VMware ESXi as hypervisor (which is why you will find `open-vm-tools` in `features/openstack/pkg.include` and why the code snippet below deals with `vmdk`-files).

If you want to run Garden Linux on OpenStack, chances are high that you will have to create your own feature set that matches your environment and your hypervisor.

## Create OpenStack Image for CC EE

Create scsi geometry image (default would be openstack)
```
qemu-img convert -f raw -O vmdk -o adapter_type=buslogic $1 $2
```

Upload image
```
openstack image create \
     --container-format bare \
     --disk-format vmdk \
     --property vmware_disktype="sparse" \
     --property vmware_adaptertype="ide" \
     --property hw_vif_model="VirtualVmxnet3" \
     --property vmware_ostype=otherLinux64Guest \
     trusty-cloud < trusty-server-cloudimg-amd64-disk1.vmdk 
