## Base Syntax of Setting Identifiers

This is how a settings ID looks like:

- GL-SET-${feature}-${setting_category}-${name:-}-${number:-001}

It is constructed from the feature the setting is part of and categorized based on [Setting Categories](#setting-categories). Adding a human readbale name is is optional and may be "too long" if e.g. file paths are described. At the end an incrementing number can be added to differentiate similar settings.

## Setting Categories

- packages to exclude
- packages to install
- systemd services
  - GL-SET-${feature}-service-${service}-001
- configuration (`config`)
  - `config-initrd` - Initrd/Dracut configuration files (`/etc/dracut.conf.d/*.conf`)
    - GL-SET-${feature}-config-initrd-001
  - `config-initrd-module` - Initrd/Dracut module files (`/usr/lib/dracut/modules.d/*`)
    - GL-SET-${feature}-config-initrd-module-001
  - `config-kernel-cmdline` - Kernel command line parameters (`/etc/kernel/cmdline.d/*.cfg`)
    - GL-SET-${feature}-config-kernel-cmdline-001
  - `config-modprobe` - Kernel module configuration (`/etc/modprobe.d/*.conf`, `/etc/modules-load.d/*.conf`)
    - GL-SET-${feature}-config-modprobe-001
  - `config-sysctl` - Sysctl parameters (`/etc/sysctl.d/*.conf`)
    - GL-SET-${feature}-config-sysctl-001
  - `config-mount` - Systemd mount units (`/etc/systemd/system/*.mount`)
    - GL-SET-${feature}-config-mount-001
  - `config-timer` - Systemd timer units (`/etc/systemd/system/*.timer`)
    - GL-SET-${feature}-config-timer-001
  - `config-preset` - Systemd presets (`/etc/systemd/system-preset/*.preset`)
    - GL-SET-${feature}-config-preset-001
  - `config-resolved` - Systemd-resolved configuration (`/etc/systemd/resolved.conf.d/*`)
    - GL-SET-${feature}-config-resolved-001
  - `config-timesyncd` - Systemd-timesyncd configuration (`/etc/systemd/timesyncd.conf.d/*`)
    - GL-SET-${feature}-config-timesyncd-001
  - `config-journald` - Systemd-journald configuration (`/etc/systemd/journald.conf.d/*`)
    - GL-SET-${feature}-config-journald-001
  - `config-udev-rules` - Udev rules (`/etc/udev/rules.d/*.rules`)
    - GL-SET-${feature}-config-udev-rules-001
  - `config-network` - Network configuration (`/etc/systemd/network/*.network`, `/etc/systemd/networkd.conf.d/*`)
    - GL-SET-${feature}-config-network-001
  - `config-ssh` - SSH configuration (`/etc/ssh/*`)
    - GL-SET-${feature}-config-ssh-001
  - `config-audit` - Audit configuration (`/etc/audit/*`)
    - GL-SET-${feature}-config-audit-001
  - `config-rsyslog` - Rsyslog configuration (`/etc/rsyslog.d/*`, `/etc/rsyslog.conf`)
    - GL-SET-${feature}-config-rsyslog-001
  - `config-security` - Security settings (`/etc/security/*`)
    - GL-SET-${feature}-config-security-001
  - `config-apt` - APT configuration (`/etc/apt/*`)
    - GL-SET-${feature}-config-apt-001
  - `config-cloud` - Cloud-init configuration (`/etc/cloud/*`)
    - GL-SET-${feature}-config-cloud-001
  - `config-chrony` - Chrony configuration (`/etc/chrony/*`, `/etc/systemd/chronyd.service.d/*`)
    - GL-SET-${feature}-config-chrony-001
  - `config-repart` - Systemd-repart configuration (`/etc/repart.d/*.conf`)
    - GL-SET-${feature}-config-repart-001
  - `config-pam` - PAM configuration (`/usr/share/pam-configs/*`)
    - GL-SET-${feature}-config-pam-001
  - `config-sudoers` - Sudoers configuration (`/etc/sudoers.d/*`)
    - GL-SET-${feature}-config-sudoers-001
  - `config-file` - Generic files (fallback for files that don't fit other categories)
    - GL-SET-${feature}-config-file-001
  - `config-user` - User configuration, e.g. creating users or adding permissions
    - GL-SET-${feature}-config-file-001
  - `config-security` - Misc Security related settings
    - GL-SET-${feature}-security-001
- scripts (`script`)
  - `script` - Generic scripts
  - `script-profile` - Profile scripts (`/etc/profile.d/*.sh`)
    - GL-SET-${feature}-script-profile-001
  - `script-cron` - Cron scripts (`/var/spool/cron/*`, `/etc/cron.*/*`)
    - GL-SET-${feature}-script-cron-001

## `file.include`

For settings that are built by adding files to the image via the [`file.include`](https://github.com/gardenlinux/builder/blob/main/docs/features.md#fileinclude) mechanism, we do not want the Setting Identifiers to be part of the image itself. Therefore an additional file called `setting_ids.yaml` is parsed.

### `setting_ids.yaml`

Example:

```
setting_ids:
  file:
    include:
      - file: "/etc/systemd/network/91-default.network"
        ids:
          - GL-SET-bfpxe-config-network-001
      - file: "/etc/dracut.conf.d/20-gl-live.conf"
        ids:
          - GL-SET-bfpxe-config-initrd-001
      - file: "/usr/lib/dracut/modules.d/98gardenlinux-live/any.conf"
        ids:
          - GL-SET-bfpxe-config-initrd-module-001
      - file: "/usr/lib/dracut/modules.d/98gardenlinux-live/cleanup.sh"
        ids:
          - GL-SET-bfpxe-config-initrd-module-002
      - file: "/path/to/some/file.conf"
        ids:
          - GL-SET-feature-config-category-001
          - GL-SET-feature-config-category-002
```

Each file can have multiple setting identifiers by listing them in the `ids` array. If a file only has one identifier, it can still be specified as a single-element list.
