# What is it?

@@@

# Prerequisites

## System packages

### Linux

```bash
sudo apt-get install -y vagrant libvirt-daemon libvirt-daemon-system entr
```

### macOS

```bash
brew install vagrant libvirt @@@
```

### Vagrant plugin

```bash
vagrant plugin install vagrant-libvirt
```

### Group membership (only for Linux)

```bash
sudo usermod -aG libvirt $(whoami)
newgrp libvirt
```

# Usage

@@@
