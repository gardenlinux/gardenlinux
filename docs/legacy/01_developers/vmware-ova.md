Building an ova can be done with `bin/make-ova`.

Requirements:
* Python `3.7` minimum is required
* Mako python module must also be installed
* `qemu-tools (qemu-img)` must be installed
* VMDK image file must be in type `streamOptimized`,
see below how to convert if necessary

## Add new os

1. Retrieve OS ID

There is a list available here in the [wiki from abiquo](https://wiki.abiquo.com/display/ABI26/Guest+Operating+System+Definition+for+VMWare).

This can also be retrieved when exporting an `ovf` from a Virtual Machine.

2. In `bin/make-ova` add new OS in `GUEST_OS`

## Convert VMDK

> OVA requires stream optimized disk image file (.vmdk) so that it can
be easily streamed over a network link. This tool can convert flat disk image
or sparse disk image to stream optimized disk image, and then create OVA with
the converted stream optimized disk image by using an OVF descriptor template.

1. Check the type of the disk image

```bash
qemu-img info --output json my-disk-image.vmdk | jq '.["format-specific"].data["create-type"]'
```

If the output is `streamOptimized`, you can skip the next step.

If the output is something like `monolithicSparse` of `monolithicFlat`,
a conversion is required.

2. Convert

```bash
qemu-img convert -p -f vmdk my-disk-image.vmdk -O vmdk my-disk-image-stream-optimized.vmdk -o subformat=streamOptimized
```

## Make ova

Specify the `vmdk`, the full path to the `template`
and the `guest-id` of the OS.

```bash
$ ./make-ova --vmdk garden-linux-27.1.0.vmdk \
           --template /gardenlinux/features/vmware/vmware.ovf.template \
           --guest-id debian10_64Guest
garden-linux-27.1.0.ova
```

## Upload template

### via UI

Navigate to the directory target, right click: `Deploy OVF template`

### with `govc`

Export the minimum required environment variables
for authentication:

```bash
GOVC_URL=vCenter-instance
GOVC_USERNAME=my-user
GOVC_PASSWORD=my-password
```

Create options file that will be used for import:

```bash
$ touch ova-import-options.json
$ govc import.spec garden-linux-27.1.0.ova | jq '.' | tee ova-import-options.json
{
  "DiskProvisioning": "flat",
  "IPAllocationPolicy": "dhcpPolicy",
  "IPProtocol": "IPv4",
  "PropertyMapping": [
    {
      "Key": "instance-id",
      "Value": "id-ovf"
    },
    {
      "Key": "hostname",
      "Value": "gardenlinux"
    },
    {
      "Key": "seedfrom",
      "Value": ""
    },
    {
      "Key": "public-keys",
      "Value": ""
    },
    {
      "Key": "user-data",
      "Value": ""
    },
    {
      "Key": "password",
      "Value": ""
    }
  ],
  "NetworkMapping": [
    {
      "Name": "VM Network",
      "Network": ""
    }
  ],
  "MarkAsTemplate": false,
  "PowerOn": false,
  "InjectOvfEnv": false,
  "WaitForIP": false,
  "Name": null
}
```

Minimum requirement in `ova-import-options.json`:
* configure `DiskProvisioning` if required
* set `MarkAsTemplate` to `true`
* replace the empty network field with the appropriate
value based on your environment

Import the `.ova`:

```bash
$ govc import.ova -name garden-linux-27.1.0 \
    -dc MY_DATACENTER \
    -ds MY_DATASTORE \
    -pool MY_POOL \
    -folder MY_FOLDER \
    -options ./ova-import-options.json \
    garden-linux-27.1.0.ova 

```

The Warning :warning: can be ignored.

The following environement variables can be exported
to avoid specifying some of the command line flags:

```bash
GOVC_DATACENTER
GOVC_DATASTORE
GOVC_RESOURCE_POOL
GOVC_FOLDER
```
