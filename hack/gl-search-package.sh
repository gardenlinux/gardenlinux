#!/bin/bash

# Requirements: fzf
#   Installation of fzf documented here: https://github.com/junegunn/fzf#installation
#   - debian: sudo apt install fzf
#   - arch:  sudo pacman -S fzf
#   - osx: brew install fzf

export gls_gl_dist=$(echo "today" |fzf --header 'Enter the Garden Linux Version you are interested in, or select today' --print-query | tail -1)

# If user did not provide minor version but only a major, assume user wants: $major.0
if [ "$gls_gl_dist" != "today" ]; then
  if ! [[ "$gls_gl_dist" =~ "." ]]; then
    major=$(echo $gls_gl_dist | cut -d. -f1)
    minor=$(echo $gls_gl_dist | cut -d. -f2)
    gls_gl_dist="${major}.0"
  fi
fi  

repo_url="http://repo.gardenlinux.io/gardenlinux/dists/${gls_gl_dist}/Release?ignoreCaching=1"

# Check if repo exists for user provided garden linux version string
if curl -s $repo_url| grep -q "Error"; then
  echo "Repo does not exist for $gls_gl_dist"
  echo "  ${repo_url}"
  exit
fi

export gls_selected_arch=$(echo -e "amd64\narm64" | fzf --header 'Select Garden Linux package architecture' )
packages_file="$(curl -s http://repo.gardenlinux.io/gardenlinux/dists/${gls_gl_dist}/main/binary-${gls_selected_arch}/Packages?ignoreCaching=1)"

function filter_package_info() {
  foo=$1;
  packages_file="$(curl -s http://repo.gardenlinux.io/gardenlinux/dists/${gls_gl_dist}/main/binary-${gls_selected_arch}/Packages?ignoreCaching=1)"
  echo "$packages_file" | sed -n "/Package: $foo$/,/^$/p"
}

# fzf preview requires function to be available in spawned subshell
export -f filter_package_info
echo -e "$packages_file" | grep "^Package:.*" | fzf --multi --preview 'bash -c "filter_package_info {2}"' --header 'Select Garden Linux Package to see details on the right window. You can type to filter.'
