#!/bin/bash

# Requirements: fzf
#   Installation of fzf documented here: https://github.com/junegunn/fzf#installation
#   - debian: sudo apt install fzf
#   - arch:  sudo pacman -S fzf
#   - osx: brew install fzf

# Actions
# - search: find what packages are available in Garden Linux apt repo
# - dep-check: check if dependencies of a package are available in Garden Linux repo
# - rdepends: (EXPERIMENTAL) find what package in garden linux depends on this package
# - download: downloads the selected deb package

THIS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[@]}")")"
# shellcheck source=/dev/null
source "${THIS_DIR}/.gl-search-functions.sh"

gl_selected_os="$(echo -e "gardenlinux\ndebian\nfrom_env_var" | fzf --header 'Select OS or enter custom url (e.g. ftp.debian.org/debian)' --print-query | tail -1)"
if [ "$gl_selected_os" == "gardenlinux" ]; then
  gls_gl_dist="$(echo "today" |fzf --header 'Enter the Garden Linux Version you are interested in, or select today' --print-query | tail -1)"
  base_url="https://packages.gardenlinux.io/gardenlinux"
elif [ "$gl_selected_os" == "debian" ]; then
  base_url="https://ftp.debian.org/debian"
  gls_gl_dist="$(echo -e "bookworm\nsid\nbullseye" |fzf --header 'Enter the Version you are interested in' --print-query | tail -1)"
elif [ "$gl_selected_os" == "from_env_var" ]; then
  if [ -z ${base_url+x} ]; then
    echo "base_url not set."
    exit
  fi
else
  gls_gl_dist="$(echo "" |fzf --header 'Enter the Version you are interested in' --print-query | tail -1)"
  base_url="$gl_selected_os"
fi


export gls_gl_dist

gl_selected_action="$(echo -e "search\ndep-check\nrdepends\ndownload" | fzf --header 'Select Action' )"
# If user did not provide minor version but only a major, assume user wants: $major.0
if [ "$gls_gl_dist" != "today" ]; then
  if ! [[ "$gls_gl_dist" =~ . ]]; then
    major=$(echo "$gls_gl_dist" | cut -d. -f1)
    #minor=$(echo "$gls_gl_dist" | cut -d. -f2)
    gls_gl_dist="${major}.0"
  fi
fi  

repo_url="$base_url/dists/${gls_gl_dist}/InRelease"

# Check if repo exists for user provided garden linux version string
if curl -s "$repo_url" | grep -q "Error"; then
  echo "Repo does not exist for $gls_gl_dist"
  echo "  ${repo_url}"
  exit
fi

gls_selected_arch="$(echo -e "amd64\narm64" | fzf --header 'Select Garden Linux package architecture' )"
export gls_selected_arch
packages_file=$(mktemp)
export packages_file
trap 'rm -rf -- "$packages_file"' EXIT

packages_url_base="$base_url/dists/${gls_gl_dist}/main/binary-${gls_selected_arch}"

# If packages raw exist, use it
if curl -s -o /dev/null -w "%{http_code}" "$packages_url_base/Packages" | grep -q 200; then
  curl -s "$packages_url_base/Packages" > "$packages_file"
elif curl -s -o /dev/null -w "%{http_code}" "$packages_url_base/Packages.gz" | grep -q 200; then
  packages_file_compressed=$(mktemp)
  curl -s "$packages_url_base/Packages.gz" > "$packages_file_compressed"
  gunzip -c "$packages_file_compressed" > "$packages_file"
else
  echo "No Packacges file found in $packages_url_base"
  exit
fi

export packages_file

case "$gl_selected_action" in
  "dep-check")
    grep "^Package:.*" "$packages_file" |  cut -d' ' -f 2 | \
      fzf \
      --multi \
      --preview "bash -c \"source ${THIS_DIR}/.gl-search-functions.sh; packages_file=$packages_file dependency_search {1}\"" \
      --header 'Select Garden Linux Package to see details on the right window. You can type to filter.'
    ;;
  "download")
    selected_pkg=$(grep "^Package:.*" "$packages_file" | cut -d' ' -f 2 | \
      fzf --header 'Select Garden Linux Package you want to download.')
    filename=$(get_filename "$selected_pkg")
    if [ -z "$filename" ]; then
      echo "No file found for $selected_pkg"
    else
      wget "$base_url/$filename"
    fi
    ;;
  "search")
    grep "^Package:.*" "$packages_file" | cut -d' ' -f 2 | \
      fzf \
      --multi \
      --preview "bash -c \"source ${THIS_DIR}/.gl-search-functions.sh; packages_file=$packages_file filter_package_info {1}\""\
      --header 'Select Garden Linux Package to see details on the right window. You can type to filter.'
    ;;
  "rdepends")
    grep "^Package:.*" "$packages_file" | cut -d' ' -f 2 | \
      fzf \
      --multi \
      --preview "bash -c \"source ${THIS_DIR}/.gl-search-functions.sh; packages_file=$packages_file rdepends_package {1}\"" \
      --header 'Select Garden Linux Package to see details on the right window. You can type to filter.'
    ;;
  *)
    echo "Unknown action..."
    ;;
esac
