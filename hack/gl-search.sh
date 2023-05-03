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

gl_selected_action="$(echo -e "search\ndep-check\nrdepends\ndownload" | fzf --header 'Select Action' )"
gls_gl_dist="$(echo "today" |fzf --header 'Enter the Garden Linux Version you are interested in, or select today' --print-query | tail -1)"
export gls_gl_dist

# If user did not provide minor version but only a major, assume user wants: $major.0
if [ "$gls_gl_dist" != "today" ]; then
  if ! [[ "$gls_gl_dist" =~ . ]]; then
    major=$(echo "$gls_gl_dist" | cut -d. -f1)
    #minor=$(echo "$gls_gl_dist" | cut -d. -f2)
    gls_gl_dist="${major}.0"
  fi
fi  

base_url="http://repo.gardenlinux.io/gardenlinux"
repo_url="$base_url/dists/${gls_gl_dist}/Release?ignoreCaching=1"

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
curl -s "$base_url/dists/${gls_gl_dist}/main/binary-${gls_selected_arch}/Packages?ignoreCaching=1" > "$packages_file"

export packages_file

function filter_package_info() {
  pkg=$1;
  sed -n "/Package: $pkg$/,/^$/p" "$packages_file"
}

function get_dependencies(){
  pkg=$1;
  sed -n "/Package: $pkg$/,/^$/p" "$packages_file" | grep "^Depends:" | sed -e "s/^Depends://" | sed -e "s/(.*)//" | sed -e "s/|/,/" | sed -r "s/,/ /g" 
}

function does_pkg_exist(){
  pkg=$1;

  sed -n "/Package: $pkg$/,/^$/p" "$packages_file" | grep -q "Package"  
}

function dependency_search(){
  dependencies="$(get_dependencies "$1"  | sed -r "s/,/ /g")"

  for dep in ${dependencies}
  do
    if does_pkg_exist "$dep"; then
      echo "Covered Dependency: $dep"
    else 
      echo "Foreign Dependency: $dep"
    fi
  done
}

function get_packages(){
    grep "^Package: " "$packages_file"
}


function rdepends_package(){
  pkg="$1"
  gardenlinux_packages="$(get_packages "$pkg")"
  # check all garden linux packages
  for chk_pkg in ${gardenlinux_packages} 
  do
    if get_dependencies "$chk_pkg" | grep -q "$pkg"; then
      echo "Reverse Dependency: ${chk_pkg}"
    fi
  done
  
}

function get_filename(){
  pkg="$1"
  gardenlinux_packages="$(get_packages "$pkg")"
  # check all garden linux packages
  filename=$(sed -n "/Package: $pkg$/,/^$/p" "$packages_file" | grep "Filename:" | cut -d':' -f 2)
  echo "$filename" | xargs
   
}
# fzf preview requires function to be available in spawned subshell
export -f filter_package_info
export -f dependency_search
export -f get_dependencies
export -f does_pkg_exist
export -f rdepends_package
export -f get_packages
export -f get_filename
case "$gl_selected_action" in
  "dep-check")
    grep "^Package:.*" "$packages_file" |  cut -d' ' -f 2 | \
      fzf \
      --multi \
      --preview "bash -c \"packages_file=$packages_file dependency_search {1}\"" \
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
      --preview "bash -c \"packages_file=$packages_file filter_package_info {1}\""\
      --header 'Select Garden Linux Package to see details on the right window. You can type to filter.'
    ;;
  "rdepends")
    grep "^Package:.*" "$packages_file" | cut -d' ' -f 2 | \
      fzf \
      --multi \
      --preview "bash -c \"packages_file=$packages_file rdepends_package {1}\"" \
      --header 'Select Garden Linux Package to see details on the right window. You can type to filter.'
    ;;
  *)
    echo "Unknown action..."
    ;;
esac
