# Building a Garden Linux Image

Building a Garden Linux image is a straightforward process, thanks to the Garden Linux builder. This guide will walk you through the steps to create your custom Garden Linux image.

## Prerequisites

1. Ensure you have the necessary dependencies installed. Refer to the [builder's README](https://github.com/gardenlinux/builder#readme) for a list of required tools and their installation instructions.
2. Clone the Garden Linux repository:
   ```bash
   git clone https://github.com/gardenlinux/gardenlinux.git
   ```

## Building the Image

1. Navigate to the Garden Linux directory:
   ```bash
   cd gardenlinux
   ```

2. Use the `build` command to start the image creation process. You can specify the target platform and other configurations as arguments. For a list of available options, refer to the [builder's documentation](https://github.com/gardenlinux/builder#readme).
   ```bash
   ./build <target-platform> <other-options>
   ```

3. Once the build process is complete, you'll find the generated image in the `output/` directory.

## Advanced Configurations

Garden Linux builder offers a range of configurations to tailor the image to specific needs:

- **Features**: Garden Linux supports a variety of features that can be included or excluded from the build. Refer to the [features documentation](https://github.com/gardenlinux/gardenlinux/tree/main/features) for a comprehensive list and their descriptions.

- **Custom Kernel**: You can specify a custom kernel during the build process. For more details, check the [kernel documentation](https://github.com/gardenlinux/gardenlinux/blob/docs-refactor-docsfolder/docs/00_introduction/kernel.md).

- **Platform-Specific Builds**: Garden Linux can be built for various platforms like AWS, Azure, GCP, and more. The builder allows you to specify the target platform for the image. Refer to the [platforms documentation](https://github.com/gardenlinux/gardenlinux/tree/main/features) for more information.

## Troubleshooting

If you encounter any issues during the build process, refer to the [Garden Linux builder's troubleshooting section](https://github.com/gardenlinux/builder#troubleshooting) for guidance.

