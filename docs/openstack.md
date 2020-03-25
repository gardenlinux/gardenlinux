# Create OpenStack Image for CC EE

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