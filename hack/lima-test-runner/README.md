# lima-vm based test harness for running Garden Linux tests

This is an experimental setup to enable experimenting with the Garden Linux test framework quickly.

## Step 1: Start an instance from an existing image, or build your own image according to your needs

Variant A: Start an instance from an existing image:

```bash
limactl start --name gardenlinux-instance-under-test hack/lima-test-runner/today.yaml
```

Variant B: Build your own image with the `lima` feature and any features you need for your tests, for example:

```bash
./build sapmachine-lima-arm64-today-local.qcow2
# edit hack/lima-test-runner/custom.yaml to include the actual path of your image
limactl start --name gardenlinux-instance-under-test hack/lima-test-runner/custom.yaml
```

## Step 2: Run the tests

Run tests:

```bash
limactl shell gardenlinux-instance-under-test ./run-tests.sh
```
