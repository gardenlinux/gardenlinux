# Development environment for Garden Linux using [lima](https://github.com/lima-vm/lima)

This is intended to be used with the [VS Code SSH Remote plugin](https://code.visualstudio.com/docs/remote/ssh)

This development environment is supposed to be stateless, disposable and reprovisionable.

## Usage instructions
- Make sure lima and qemu are installed.
- Run the following commands:

```bash
limactl create --name gl-dev hack/lima-dev-env/gl-dev.yaml
echo "Include ${LIMA_HOME:-$HOME/.lima}/gl-dev/ssh.config" >> ~/.ssh/config
limactl start gl-dev
```

- Connect to host 'lima-gl-dev' in VS Code via the SSH Remote plugin
- In the VS Code window connected ot the host 'lima-gl-dev', open the `~/gardenlinux` folder which contains a clone of the Garden Linux git repo
- Perform the required git configuration to be able to commit and push code
    - Configure your name and email
    - Configure a GitHub personal access token
