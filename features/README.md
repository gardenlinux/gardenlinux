# Features

<website-features>

## General
Each folder represents a usable Garden Linux `feature` that can be added to a final Garden Linux artifact. This allows you to build Garden Linux for different cloud platforms with a different set of features like `CIS`, `read only` etc. Currently, the following feature types are available:

| Feature Type | Feature Name |
|---|---|
| Platform | ali, aws, azure, gcp, kvm, baremetal, ... |
| Feature | container host, virtual host, ... |
| Modifier | _slim, _readonly, _pxe, _iso, ... |
| Element | cis, fedramp, ... |

*Keep in mind that `not all features` may be combined together. However, features may in-/exclude other features or block the build process by given exclusive/incompatible feature combinations.*

## Selecting Features
 Desired features can be selected in the two ways.

 * Editing the [Makefile](../Makefile)
 * Explicit calling of `./build.sh --features <feature1\>,<feature2\>`

 ### Editing the [Makefile](../Makefile)
 The recommended way to change the features is by adjusting the [Makefile](../Makefile). This ensures the compability with our [documentation](../docs). Therefore, you may just change the block of your desired artifact.

 **Example:**

 If you want to add the `CIS` feature for `kvm-dev` you may adjust the [Makefile](../Makefile):

 From:
 ```
kvm-dev: container-build cert/sign.pub
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,kvm,_dev $(BUILDDIR) $(VERSION)
```
 To:
 ```
kvm-dev: container-build cert/sign.pub
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,kvm,cis,_dev $(BUILDDIR) $(VERSION)
```

Afterwards, the artifact can be created by executing `make kvm-dev`.


### Explicit Calling of `./build.sh --features <feature1\>,<feature2\>`
This method is slightly different from the first one and results in calling the `build.sh` directly, which is even called from the [Makefile](../Makefile). Within this method features can be directly given via the `cli`.

**Example:**

`./build.sh --features <feature1\>,<feature2\> [...]`

## Details
More details and examples for each option can be found within the [example/](example/README.md) folder.