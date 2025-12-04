# What is it?

@@@

# Prerequisites

## Packages

### Linux (vagrant vm engine)

```bash
sudo apt-get install -y vagrant libvirt-daemon libvirt-daemon-system
```

### Linux (lima vm engine)

```bash
asdf plugin add lima
asdf install lima 2.0.2
asdf set lima 2.0.2
```

### Linux (optional packages)

For `--watch` mode to work you will need `entr`:

```bash
sudo apt-get install -y entr
```

### macOS (vagrant vm engine)

```bash
brew install vagrant libvirt @@@
```

### macOS (lima vm engine)

```bash
brew install lima
```

### Vagrant plugin (only if using vagrant vm engine)

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
