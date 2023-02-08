#!/bin/bash

# Requirements: fzf
#   Installation of fzf documented here: https://github.com/junegunn/fzf#installation
#   - debian: sudo apt install fzf
#   - arch:  sudo pacman -S fzf
#   - osx: brew install fzf

# Select Garden Linux Distribution by setting env variable "gl_dist=934.3"
# Default: today


# TODO:
# - user select architecture via fzf 
# - user select version via fzf

export gls_selected_arch=$(echo -e "amd64\narm64" | fzf --header 'Select Garden Linux package architecture' )


export gls_gl_dist="${gl_dist:-today}"
packages_file="$(curl -s http://repo.gardenlinux.io/gardenlinux/dists/${gls_gl_dist}/main/binary-${gls_selected_arch}/Packages)"

function filter_package_info() {
  foo=$1;
  packages_file="$(curl -s http://repo.gardenlinux.io/gardenlinux/dists/${gls_gl_dist}/main/binary-${gls_selected_arch}/Packages)"
  echo "$packages_file" | sed -n "/Package: $foo$/,/^$/p"
}

# fzf preview requires function to be available in spawned subshell
export -f filter_package_info
echo -e "$packages_file" | grep "^Package:.*" | fzf --multi --preview 'bash -c "filter_package_info {2}"' --header 'Select Garden Linux Package to see details on the right window. You can type to filter.'
