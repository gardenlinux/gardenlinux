#!/bin/bash

# Requirements: fzf
#   Installation of fzf documented here: https://github.com/junegunn/fzf#installation
#   - debian: sudo apt install fzf
#   - arch:  sudo pacman -S fzf
#   - osx: brew install fzf

show_help() {
    cat <<EOF
Usage: $(basename "$0") [--help]

Browse CVE information from GLVD.

Options:
    --help    Show this help message and exit.

Environment variables:
    GLVD_URL  Set the GLVD endpoint (default: https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/)
EOF
}

if [[ "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Select Garden Linux version using fzf
GL_VERSIONS=("1592.10" "1877.0")
SELECTED_VERSION=$(printf "%s\n" "${GL_VERSIONS[@]}" | fzf --prompt="Select Garden Linux version: ")

if [[ -z "$SELECTED_VERSION" ]]; then
    echo "No version selected. Exiting."
    exit 1
fi

GLVD_URL="${GLVD_URL:-https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/}"

SELECTED_LINE=$(curl -s "${GLVD_URL}v1/cves/$SELECTED_VERSION" | jq -r '
    to_entries[] |
    "\(.value.cveId) | \(.value.baseScore) | \(.value.sourcePackageName) | \(.value.sourcePackageVersion)"
' | fzf --header="CVE ID | CVSS Base Score | Source Package Name | Source Package Version")

if [[ -z "$SELECTED_LINE" ]]; then
    echo "No CVE selected. Exiting."
    exit 1
fi

CVE_ID=$(echo "$SELECTED_LINE" | awk -F' | ' '{print $1}')
echo "Selected CVE ID: $CVE_ID"

curl -s "${GLVD_URL}v1/cveDetails/${CVE_ID}" | jq -r '
.details as $d |
"CVE ID: \($d.cveId)
Status: \($d.vulnStatus | gsub("^\"|\"$";""))
Published: \($d.cvePublishedDate | gsub("^\"|\"$";""))
Modified: \($d.cveModifiedDate | gsub("^\"|\"$";""))
Description: \($d.description | gsub("^\"|\"$";""))

Affected Versions:" ,
([range(0; ($d.distro|length)) as $i |
  "  - \($d.distro[$i]) \($d.distroVersion[$i]): \($d.sourcePackageName[$i]) \($d.sourcePackageVersion[$i]) | Vulnerable: \($d.isVulnerable[$i])"
] | .[])
'
