#!/bin/bash


function filter_package_info() {
  pkg=$1;
  if [ -z "${packages_file}" ]; then
    echo "Error: The variable 'packages_file' is not set or is empty."
    exit 1
  fi
  sed -n "/Package: $pkg$/,/^$/p" "$packages_file"
}

function get_dependencies(){
  pkg=$1;
  if [ -z "${packages_file}" ]; then
    echo "Error: The variable 'packages_file' is not set or is empty."
    exit 1
  fi
  sed -n "/Package: $pkg$/,/^$/p" "$packages_file" | grep "^Depends:" | sed -e "s/^Depends://" | sed -e "s/(.*)//" | sed -e "s/|/,/" | sed -r "s/,/ /g" 
}

function does_pkg_exist(){
  pkg=$1;
  if [ -z "${packages_file}" ]; then
    echo "Error: The variable 'packages_file' is not set or is empty."
    exit 1
  fi
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
    if [ -z "${packages_file}" ]; then
        echo "Error: The variable 'packages_file' is not set or is empty."
        exit 1
    fi
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
  if [ -z "${packages_file}" ]; then
    echo "Error: The variable 'packages_file' is not set or is empty."
    exit 1
  fi
  # check all garden linux packages
  filename=$(sed -n "/Package: $pkg$/,/^$/p" "$packages_file" | grep "Filename:" | cut -d':' -f 2)
  echo "$filename" | xargs
   
}