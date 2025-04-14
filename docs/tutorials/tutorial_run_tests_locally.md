# Tutorial: Run tests locally 

You want to test a specific Garden Linux flavour locally? This tutorial is for you. 
We will walk through the local test process, and assume you are already familiar with building Garden Linux images.

TODO: insert link to tutorial to build images here

First, we need to know the flavour of Garden Linux that we want to test. (for example `kvm-gardener_prod-amd64`) 
In a later bonus lesson we will test a custom image not defined in flavour.yaml (yet).  

Typically, when you have the task to test something locally you already know the target, but if you need to pick a target, you can get a list of all officially supported test targets by running

```bash
make --directory=tests/
```
which will read the flavours.yaml and parse it to generate the list of Make targets you can execute. Try it!

<details>
  <summary>Example output</summary>
  <pre>Usage: make [target]

  general targets:
  help					List available tasks of the project                                     
  all					Run all platform tests                                                   

  Available Chroot Test targets for Official Flavors:

  base Chroot tests targets:
    base-amd64-chroot-test                                                        Run bootstrap/base Chroot tests for amd64
    base-arm64-chroot-test                                                        Run bootstrap/base Chroot tests for arm64
    container-amd64-chroot-test                                                   Run base container Chroot tests for amd64
    container-arm64-chroot-test                                                   Run base container Chroot tests for arm64

  bare flavor Container tests targets:
    bare-libc-amd64-container-test                                                Run Container tests bare-libc-amd64
    bare-libc-arm64-container-test                                                Run Container tests bare-libc-arm64
    bare-nodejs-amd64-container-test                                              Run Container tests bare-nodejs-amd64
    bare-nodejs-arm64-container-test                                              Run Container tests bare-nodejs-arm64
    bare-python-amd64-container-test                                              Run Container tests bare-python-amd64
    bare-python-arm64-container-test                                              Run Container tests bare-python-arm64
    bare-sapmachine-amd64-container-test                                          Run Container tests bare-sapmachine-amd64
    bare-sapmachine-arm64-container-test                                          Run Container tests bare-sapmachine-arm64

  image flavor Chroot tests targets:
    ali-gardener_prod-amd64-chroot-test                                           Run Chroot tests ali-gardener_prod-amd64
    aws-gardener_prod-amd64-chroot-test                                           Run Chroot tests aws-gardener_prod-amd64
    aws-gardener_prod-arm64-chroot-test                                           Run Chroot tests aws-gardener_prod-arm64
    aws-gardener_prod_tpm2_trustedboot-amd64-chroot-test                          Run Chroot tests aws-gardener_prod_tpm2_trustedboot-amd64
    aws-gardener_prod_tpm2_trustedboot-arm64-chroot-test                          Run Chroot tests aws-gardener_prod_tpm2_trustedboot-arm64
    aws-gardener_prod_trustedboot-amd64-chroot-test                               Run Chroot tests aws-gardener_prod_trustedboot-amd64
    aws-gardener_prod_trustedboot-arm64-chroot-test                               Run Chroot tests aws-gardener_prod_trustedboot-arm64
    azure-gardener_prod-amd64-chroot-test                                         Run Chroot tests azure-gardener_prod-amd64
    azure-gardener_prod-arm64-chroot-test                                         Run Chroot tests azure-gardener_prod-arm64
    azure-gardener_prod_tpm2_trustedboot-amd64-chroot-test                        Run Chroot tests azure-gardener_prod_tpm2_trustedboot-amd64
    azure-gardener_prod_tpm2_trustedboot-arm64-chroot-test                        Run Chroot tests azure-gardener_prod_tpm2_trustedboot-arm64
    azure-gardener_prod_trustedboot-amd64-chroot-test                             Run Chroot tests azure-gardener_prod_trustedboot-amd64
    azure-gardener_prod_trustedboot-arm64-chroot-test                             Run Chroot tests azure-gardener_prod_trustedboot-arm64
    container-amd64-chroot-test                                                   Run Chroot tests container-amd64
    container-arm64-chroot-test                                                   Run Chroot tests container-arm64
    gcp-gardener_prod-amd64-chroot-test                                           Run Chroot tests gcp-gardener_prod-amd64
    gcp-gardener_prod-arm64-chroot-test                                           Run Chroot tests gcp-gardener_prod-arm64
    gcp-gardener_prod_tpm2_trustedboot-amd64-chroot-test                          Run Chroot tests gcp-gardener_prod_tpm2_trustedboot-amd64
    gcp-gardener_prod_tpm2_trustedboot-arm64-chroot-test                          Run Chroot tests gcp-gardener_prod_tpm2_trustedboot-arm64
    gcp-gardener_prod_trustedboot-amd64-chroot-test                               Run Chroot tests gcp-gardener_prod_trustedboot-amd64
    gcp-gardener_prod_trustedboot-arm64-chroot-test                               Run Chroot tests gcp-gardener_prod_trustedboot-arm64
    gdch-gardener_prod-amd64-chroot-test                                          Run Chroot tests gdch-gardener_prod-amd64
    gdch-gardener_prod-arm64-chroot-test                                          Run Chroot tests gdch-gardener_prod-arm64
    kvm-gardener_prod-amd64-chroot-test                                           Run Chroot tests kvm-gardener_prod-amd64
    kvm-gardener_prod-arm64-chroot-test                                           Run Chroot tests kvm-gardener_prod-arm64
    kvm-gardener_prod_tpm2_trustedboot-amd64-chroot-test                          Run Chroot tests kvm-gardener_prod_tpm2_trustedboot-amd64
    kvm-gardener_prod_tpm2_trustedboot-arm64-chroot-test                          Run Chroot tests kvm-gardener_prod_tpm2_trustedboot-arm64
    kvm-gardener_prod_trustedboot-amd64-chroot-test                               Run Chroot tests kvm-gardener_prod_trustedboot-amd64
    kvm-gardener_prod_trustedboot-arm64-chroot-test                               Run Chroot tests kvm-gardener_prod_trustedboot-arm64
    metal-capi-amd64-chroot-test                                                  Run Chroot tests metal-capi-amd64
    metal-capi-arm64-chroot-test                                                  Run Chroot tests metal-capi-arm64
    metal-gardener_prod-amd64-chroot-test                                         Run Chroot tests metal-gardener_prod-amd64
    metal-gardener_prod-arm64-chroot-test                                         Run Chroot tests metal-gardener_prod-arm64
    metal-gardener_prod_tpm2_trustedboot-amd64-chroot-test                        Run Chroot tests metal-gardener_prod_tpm2_trustedboot-amd64
    metal-gardener_prod_tpm2_trustedboot-arm64-chroot-test                        Run Chroot tests metal-gardener_prod_tpm2_trustedboot-arm64
    metal-gardener_prod_trustedboot-amd64-chroot-test                             Run Chroot tests metal-gardener_prod_trustedboot-amd64
    metal-gardener_prod_trustedboot-arm64-chroot-test                             Run Chroot tests metal-gardener_prod_trustedboot-arm64
    metal-gardener_pxe-amd64-chroot-test                                          Run Chroot tests metal-gardener_pxe-amd64
    metal-gardener_pxe-arm64-chroot-test                                          Run Chroot tests metal-gardener_pxe-arm64
    metal-vhost-amd64-chroot-test                                                 Run Chroot tests metal-vhost-amd64
    metal-vhost-arm64-chroot-test                                                 Run Chroot tests metal-vhost-arm64
    metal_pxe-amd64-chroot-test                                                   Run Chroot tests metal_pxe-amd64
    metal_pxe-arm64-chroot-test                                                   Run Chroot tests metal_pxe-arm64
    openstack-gardener_prod-amd64-chroot-test                                     Run Chroot tests openstack-gardener_prod-amd64
    openstack-gardener_prod-arm64-chroot-test                                     Run Chroot tests openstack-gardener_prod-arm64
    openstackbaremetal-gardener_prod-amd64-chroot-test                            Run Chroot tests openstackbaremetal-gardener_prod-amd64
    openstackbaremetal-gardener_prod-arm64-chroot-test                            Run Chroot tests openstackbaremetal-gardener_prod-arm64
    vmware-gardener_prod-amd64-chroot-test                                        Run Chroot tests vmware-gardener_prod-amd64
    vmware-gardener_prod-arm64-chroot-test                                        Run Chroot tests vmware-gardener_prod-arm64

  Available Platform Test targets for Official Flavors:

  Qemu Provisioner Platform Tests targets:
    ali-gardener_prod-amd64-qemu-test-platform                                    Run platform tests build with Qemu for ali-gardener_prod-amd64
    aws-gardener_prod-amd64-qemu-test-platform                                    Run platform tests build with Qemu for aws-gardener_prod-amd64
    aws-gardener_prod-arm64-qemu-test-platform                                    Run platform tests build with Qemu for aws-gardener_prod-arm64
    aws-gardener_prod_tpm2_trustedboot-amd64-qemu-test-platform                   Run platform tests build with Qemu for aws-gardener_prod_tpm2_trustedboot-amd64
    aws-gardener_prod_tpm2_trustedboot-arm64-qemu-test-platform                   Run platform tests build with Qemu for aws-gardener_prod_tpm2_trustedboot-arm64
    aws-gardener_prod_trustedboot-amd64-qemu-test-platform                        Run platform tests build with Qemu for aws-gardener_prod_trustedboot-amd64
    aws-gardener_prod_trustedboot-arm64-qemu-test-platform                        Run platform tests build with Qemu for aws-gardener_prod_trustedboot-arm64
    azure-gardener_prod-amd64-qemu-test-platform                                  Run platform tests build with Qemu for azure-gardener_prod-amd64
    azure-gardener_prod-arm64-qemu-test-platform                                  Run platform tests build with Qemu for azure-gardener_prod-arm64
    azure-gardener_prod_tpm2_trustedboot-amd64-qemu-test-platform                 Run platform tests build with Qemu for azure-gardener_prod_tpm2_trustedboot-amd64
    azure-gardener_prod_tpm2_trustedboot-arm64-qemu-test-platform                 Run platform tests build with Qemu for azure-gardener_prod_tpm2_trustedboot-arm64
    azure-gardener_prod_trustedboot-amd64-qemu-test-platform                      Run platform tests build with Qemu for azure-gardener_prod_trustedboot-amd64
    azure-gardener_prod_trustedboot-arm64-qemu-test-platform                      Run platform tests build with Qemu for azure-gardener_prod_trustedboot-arm64
    container-amd64-qemu-test-platform                                            Run platform tests build with Qemu for container-amd64
    container-arm64-qemu-test-platform                                            Run platform tests build with Qemu for container-arm64
    gcp-gardener_prod-amd64-qemu-test-platform                                    Run platform tests build with Qemu for gcp-gardener_prod-amd64
    gcp-gardener_prod-arm64-qemu-test-platform                                    Run platform tests build with Qemu for gcp-gardener_prod-arm64
    gcp-gardener_prod_tpm2_trustedboot-amd64-qemu-test-platform                   Run platform tests build with Qemu for gcp-gardener_prod_tpm2_trustedboot-amd64
    gcp-gardener_prod_tpm2_trustedboot-arm64-qemu-test-platform                   Run platform tests build with Qemu for gcp-gardener_prod_tpm2_trustedboot-arm64
    gcp-gardener_prod_trustedboot-amd64-qemu-test-platform                        Run platform tests build with Qemu for gcp-gardener_prod_trustedboot-amd64
    gcp-gardener_prod_trustedboot-arm64-qemu-test-platform                        Run platform tests build with Qemu for gcp-gardener_prod_trustedboot-arm64
    gdch-gardener_prod-amd64-qemu-test-platform                                   Run platform tests build with Qemu for gdch-gardener_prod-amd64
    gdch-gardener_prod-arm64-qemu-test-platform                                   Run platform tests build with Qemu for gdch-gardener_prod-arm64
    kvm-gardener_prod-amd64-qemu-test-platform                                    Run platform tests build with Qemu for kvm-gardener_prod-amd64
    kvm-gardener_prod-arm64-qemu-test-platform                                    Run platform tests build with Qemu for kvm-gardener_prod-arm64
    kvm-gardener_prod_tpm2_trustedboot-amd64-qemu-test-platform                   Run platform tests build with Qemu for kvm-gardener_prod_tpm2_trustedboot-amd64
    kvm-gardener_prod_tpm2_trustedboot-arm64-qemu-test-platform                   Run platform tests build with Qemu for kvm-gardener_prod_tpm2_trustedboot-arm64
    kvm-gardener_prod_trustedboot-amd64-qemu-test-platform                        Run platform tests build with Qemu for kvm-gardener_prod_trustedboot-amd64
    kvm-gardener_prod_trustedboot-arm64-qemu-test-platform                        Run platform tests build with Qemu for kvm-gardener_prod_trustedboot-arm64
    metal-capi-amd64-qemu-test-platform                                           Run platform tests build with Qemu for metal-capi-amd64
    metal-capi-arm64-qemu-test-platform                                           Run platform tests build with Qemu for metal-capi-arm64
    metal-gardener_prod-amd64-qemu-test-platform                                  Run platform tests build with Qemu for metal-gardener_prod-amd64
    metal-gardener_prod-arm64-qemu-test-platform                                  Run platform tests build with Qemu for metal-gardener_prod-arm64
    metal-gardener_prod_tpm2_trustedboot-amd64-qemu-test-platform                 Run platform tests build with Qemu for metal-gardener_prod_tpm2_trustedboot-amd64
    metal-gardener_prod_tpm2_trustedboot-arm64-qemu-test-platform                 Run platform tests build with Qemu for metal-gardener_prod_tpm2_trustedboot-arm64
    metal-gardener_prod_trustedboot-amd64-qemu-test-platform                      Run platform tests build with Qemu for metal-gardener_prod_trustedboot-amd64
    metal-gardener_prod_trustedboot-arm64-qemu-test-platform                      Run platform tests build with Qemu for metal-gardener_prod_trustedboot-arm64
    metal-gardener_pxe-amd64-qemu-test-platform                                   Run platform tests build with Qemu for metal-gardener_pxe-amd64
    metal-gardener_pxe-arm64-qemu-test-platform                                   Run platform tests build with Qemu for metal-gardener_pxe-arm64
    metal-vhost-amd64-qemu-test-platform                                          Run platform tests build with Qemu for metal-vhost-amd64
    metal-vhost-arm64-qemu-test-platform                                          Run platform tests build with Qemu for metal-vhost-arm64
    metal_pxe-amd64-qemu-test-platform                                            Run platform tests build with Qemu for metal_pxe-amd64
    metal_pxe-arm64-qemu-test-platform                                            Run platform tests build with Qemu for metal_pxe-arm64
    openstack-gardener_prod-amd64-qemu-test-platform                              Run platform tests build with Qemu for openstack-gardener_prod-amd64
    openstack-gardener_prod-arm64-qemu-test-platform                              Run platform tests build with Qemu for openstack-gardener_prod-arm64
    openstackbaremetal-gardener_prod-amd64-qemu-test-platform                     Run platform tests build with Qemu for openstackbaremetal-gardener_prod-amd64
    openstackbaremetal-gardener_prod-arm64-qemu-test-platform                     Run platform tests build with Qemu for openstackbaremetal-gardener_prod-arm64
    vmware-gardener_prod-amd64-qemu-test-platform                                 Run platform tests build with Qemu for vmware-gardener_prod-amd64
    vmware-gardener_prod-arm64-qemu-test-platform                                 Run platform tests build with Qemu for vmware-gardener_prod-arm64

  Tofu Provisioner Platform Tests targets:
    ali-gardener_prod-amd64-tofu-test-platform                                    Run platform tests build with OpenTofu for ali-gardener_prod-amd64
    aws-gardener_prod-amd64-tofu-test-platform                                    Run platform tests build with OpenTofu for aws-gardener_prod-amd64
    aws-gardener_prod-arm64-tofu-test-platform                                    Run platform tests build with OpenTofu for aws-gardener_prod-arm64
    aws-gardener_prod_tpm2_trustedboot-amd64-tofu-test-platform                   Run platform tests build with OpenTofu for aws-gardener_prod_tpm2_trustedboot-amd64
    aws-gardener_prod_tpm2_trustedboot-arm64-tofu-test-platform                   Run platform tests build with OpenTofu for aws-gardener_prod_tpm2_trustedboot-arm64
    aws-gardener_prod_trustedboot-amd64-tofu-test-platform                        Run platform tests build with OpenTofu for aws-gardener_prod_trustedboot-amd64
    aws-gardener_prod_trustedboot-arm64-tofu-test-platform                        Run platform tests build with OpenTofu for aws-gardener_prod_trustedboot-arm64
    azure-gardener_prod-amd64-tofu-test-platform                                  Run platform tests build with OpenTofu for azure-gardener_prod-amd64
    azure-gardener_prod-arm64-tofu-test-platform                                  Run platform tests build with OpenTofu for azure-gardener_prod-arm64
    azure-gardener_prod_tpm2_trustedboot-amd64-tofu-test-platform                 Run platform tests build with OpenTofu for azure-gardener_prod_tpm2_trustedboot-amd64
    azure-gardener_prod_tpm2_trustedboot-arm64-tofu-test-platform                 Run platform tests build with OpenTofu for azure-gardener_prod_tpm2_trustedboot-arm64
    azure-gardener_prod_trustedboot-amd64-tofu-test-platform                      Run platform tests build with OpenTofu for azure-gardener_prod_trustedboot-amd64
    azure-gardener_prod_trustedboot-arm64-tofu-test-platform                      Run platform tests build with OpenTofu for azure-gardener_prod_trustedboot-arm64
    gcp-gardener_prod-amd64-tofu-test-platform                                    Run platform tests build with OpenTofu for gcp-gardener_prod-amd64
    gcp-gardener_prod-arm64-tofu-test-platform                                    Run platform tests build with OpenTofu for gcp-gardener_prod-arm64
    gcp-gardener_prod_tpm2_trustedboot-amd64-tofu-test-platform                   Run platform tests build with OpenTofu for gcp-gardener_prod_tpm2_trustedboot-amd64
    gcp-gardener_prod_tpm2_trustedboot-arm64-tofu-test-platform                   Run platform tests build with OpenTofu for gcp-gardener_prod_tpm2_trustedboot-arm64
    gcp-gardener_prod_trustedboot-amd64-tofu-test-platform                        Run platform tests build with OpenTofu for gcp-gardener_prod_trustedboot-amd64
    gcp-gardener_prod_trustedboot-arm64-tofu-test-platform                        Run platform tests build with OpenTofu for gcp-gardener_prod_trustedboot-arm64
  </pre>
</details>


Great. You see a lot of test potential test targets now. You know the name of the image you want to test(we continue with `kvm-gardener_prod`), and you know the architecture of the image you want to test (we continue with `amd64`).

We have the full name of the Garden Linux image, for example `kvm-gardener_prod-amd64`

But the make targets list a lot more than just the flavours? which one to pick? This is easy once you understand the different methods to run the Garden Linux VM we want to test. 

TODO: insert link to tests/README.md

Since we want to run tests locally, we focus here on the two local options:

1. qemu
2. chroot

We use the qemu target in this tutorial, but please feel free to try out chroot also! 


Since we know what we want to test and how we want to test it, the rest is very easy.
Starting a local VM with qemu:

```bash
make --directory=tests/platformSetup <insert-your-target>-qemu-apply
```
This will spawn a qemu VM in the background. If it runs successfully, we can then try to login to the VM first:

```bash
make --directory=tests/platformSetup <insert-your-target>-login
```

This VM uses the Garden Linux image you specified, so you could use this to try and test manually. We won't do this in this tutorial, but feel free to explore on the VM instance. Make sure to remember what you have changed manually inside the VM in case you still want to run the tests.


To start the python tests against this qemu VM, we do the following:
```bash
make --directory=tests <insert-your-target>-qemu-test-platform
```


And if we are done with testing we can destroy the qemu VM again. Try to find that command with the help of the help message of our makefile in `tests/platformSetup`: 
```
make --directory=tests/platformSetup
```

Now you are able to run tests locally with qemu. Key take aways of this tutorial are:
- Garden Linux flavours that can be tested are defined in flavours.yaml
- For testing images locally we can spawn and destroy a VM with make
- You can manually login to the started VM




## Bonus exercise: Running local tests of a non-official flavour
Your task is to run pytests against a local qemu VM for the `kvm_dev-<CPU arch of your choice>`
flavour.
As you have learned in this tutorial, you can spawn a qemu VM with a given Garden Linux flavour like this
```bash
make --directory=tests/platformSetup kvm-dev-<CPU arch of your choise>-qemu-apply
```
But this will fail. You know why?

<details>
  <summary>Why it fails</summary>
  Make targets parse the flavours.yaml. Only make targets exist for targets defined in the flavours.yaml
</details>

Can you make minimal changes to also run `kvm_dev` on your local machine? 

<details>
  <summary>Hint</summary>
  Edit flavours.yaml
</details>

