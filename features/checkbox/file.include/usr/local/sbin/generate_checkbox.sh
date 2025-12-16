#!/usr/bin/env bash
set -Eeufo pipefail

echo -e "=================================="
echo -e "**Welcome to checkbox initiation**"
echo -e "=================================="

### --- CONFIGURATION ---
rm -rf /root/checkbox_venv /root/checbox
: "${HOME:=/root}"
DEBIAN_RELEASE="trixie"
VENVDIR="$HOME/checkbox_venv"
CHECKBOX_REPO="https://github.com/canonical/checkbox.git"
CHK_DIRECTORIES_URL="https://raw.githubusercontent.com/saubhikdattagithub/public/main/providers_directory_working_v5.0.zip"
NOW=$(date +%Y-%m-%dT%H.%M.%S)
PROVIDER='1877.gardenlinux.certification:ccloud'
REPORT_DIR='/home/checkbox_reports'
mkdir -p $REPORT_DIR

### --- FUNCTIONS ---
configure_dns() {
    echo "==> Configuring DNS..."
    echo "nameserver 8.8.8.8" | tee /etc/resolv.conf >/dev/null
}

configure_sources() {
    echo "==> Configuring APT sources..."
    cat <<EOF > /etc/apt/sources.list
deb http://deb.debian.org/debian ${DEBIAN_RELEASE} main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian ${DEBIAN_RELEASE} main contrib non-free non-free-firmware

deb http://deb.debian.org/debian ${DEBIAN_RELEASE}-updates main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian ${DEBIAN_RELEASE}-updates main contrib non-free non-free-firmware

deb http://security.debian.org/debian-security ${DEBIAN_RELEASE}-security main contrib non-free non-free-firmware
deb-src http://security.debian.org/debian-security ${DEBIAN_RELEASE}-security main contrib non-free non-free-firmware
EOF
}

install_packages() {
    echo "==> Installing required packages..."
    apt-get clean
    rm -rf /var/lib/apt/lists/*
    apt-get update -q

    local packages=(
        snapd python3 python3-pip python3-setuptools python3-wheel
        git unzip usbutils pciutils lshw dmidecode hdparm smartmontools
        util-linux parted iproute2 iputils-ping net-tools ethtool curl debsums
        ipmitool wget sysstat stress stress-ng memtester acpid acpi-support-base
        acpi-call-dkms i2c-tools lm-sensors iozone3 python3-serial systemd-sysv
        dosfstools exfatprogs xfsprogs e2fsprogs btrfs-progs f2fs-tools upower
        powermgmt-base pulseaudio alsa-utils sox v4l-utils efibootmgr apparmor
        apparmor-utils fwupd fwupd-signed tree file jq xxd bash-completion
        libfile-fnmatch-perl iperf iperf3 nmap python3-natsort lxc bc
        ntpsec-ntpdate netcat-traditional w3m python3-virtualenv zip rsyslog
        cpanminus
    )

    DEBIAN_FRONTEND=noninteractive apt-get install -yq --fix-missing "${packages[@]}"
}

configure_profile() {
    echo "==> Updating profile..."
    cat <<'EOF' >> ~/.profile
alias chkcli='checkbox-cli'
alias chkv='cd ~/checkbox/checkbox-ng && . ../../checkbox_venv/bin/activate && cd ../providers'
alias ll='ls -lrth'
alias vim='vim -u NONE -N'
export STRESS_NG_DISK_TIME=60
export STRESS_NG_CPU_TIME=60
EOF
}

configure_logging() {
    echo "==> Configuring rsyslog..."
    mkdir -p /var/log/installer
    touch /var/log/installer/testingfile
    echo "kern.*   -/var/log/kern.log" >> /etc/rsyslog.conf
    systemctl enable --now rsyslog
}

setup_checkbox_venv() {
    set -e

    echo "==> Setting up Checkbox v5.0.0 in virtualenv..."

    # ---- variables (adjust if needed) ----
    CHECKBOX_DIR="$HOME/checkbox"
    VENVDIR="$HOME/checkbox_venv"
    CHECKBOX_REPO="https://github.com/canonical/checkbox.git"
    #CHK_DIRECTORIES_URL="https://raw.githubusercontent.com/saubhikdattagithub/public/main/chkbx_directories.zip"
    CHK_DIRECTORIES_URL="https://raw.githubusercontent.com/saubhikdattagithub/public/main/providers_directory_working_v5.0.zip"
    # -------------------------------------

    echo "==> Installing dependencies"
    sudo apt update -q
    sudo apt install -yq --fix-missing git unzip wget

    echo "==> Cloning Checkbox repo"
    rm -rf "$CHECKBOX_DIR" /root/checkbox*
    git clone "$CHECKBOX_REPO" "$CHECKBOX_DIR"

    cd "$CHECKBOX_DIR"
    git checkout tags/v5.0.0 -b v5.0.0

    echo "==> Creating virtualenv"
    cd checkbox-ng
    ./mk-venv "$VENVDIR"

    echo "==> Activating virtualenv"
    # shellcheck disable=SC1091
    . ../../checkbox_venv/bin/activate

    echo "==> Installing checkbox-support"
    cd ../checkbox-support
    pip install -e .
    pip uninstall -y urwid
    pip install "urwid<3"


    echo "==> Installing resource provider"
    cd ../providers/resource
    python3 manage.py develop

    echo "==> Replacing providers directory (if needed)"
    cd "$CHECKBOX_DIR"
    wget -O /tmp/providers_directory_working_v5.0.zip "$CHK_DIRECTORIES_URL"
    mv providers providers.ORIG
    unzip -o /tmp/providers_directory_working_v5.0.zip -d "$CHECKBOX_DIR"

    echo "==> Re-install provider after startprovider"
    cd "$CHECKBOX_DIR/providers/$PROVIDER"
    python3 manage.py develop


    echo "==> Checkbox v5.0.0 setup complete"
}

execute_test() {
    set +e

    NOW="$(date +%Y%m%d_%H%M%S)"
    VENVDIR="$HOME/checkbox_venv"

    echo "==> Executing HW test: Server Certification Full"

    # Activate Checkbox virtualenv
    # shellcheck disable=SC1091
    source "$VENVDIR/bin/activate"

    # Always use venv binary explicitly
    "$VENVDIR/bin/checkbox-cli" run \
        --non-interactive \
        --output-format html \
        --output-file "$REPORT_DIR/submission_${NOW}.html" \
        '1877.gardenlinux.certification::22.04-server-full'
	CHK_EXIT=$?

    echo "Checkbox exit code: $CHK_EXIT"

    # Success criteria = report exists
    if [ -f "$REPORT_DIR/submission_${NOW}.html" ]; then
        echo "Outcome: job passed"
        echo "Saving results to /home/checkbox_reports"
        exit 0
    else
        echo "Outcome: job failed (report not generated)"
        exit 1
    fi

}

### --- MAIN EXECUTION FLOW ---
configure_dns
configure_sources
install_packages
configure_profile
configure_logging
setup_checkbox_venv
execute_test
