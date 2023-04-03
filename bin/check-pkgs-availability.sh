#!/bin/bash
# 
# Checks if all packages defined in any pkg.include are available in garden linux apt repo
# - first parameter is path to garden linux repo root
#
# 
gardenlinux_repo_root="$1"
version=${2:-today}


cd "$gardenlinux_repo_root" || exit 1
 
function check_pkg(){
  packages_file=$1
  package=$2
  arch=$3
  package=$(eval echo "$package")
  if ! grep "^Package: $package$" -q <<< "$packages_file" ; then
    missing_packages+=("$package/$arch")
  fi

  return 
}

declare -a missing_packages=()

if curl -s "http://repo.gardenlinux.io/gardenlinux/dists/${version}/InRelease" | grep "<Error><Code>NoSuchKey</Code><Message>" -q; then
  echo "Apt Dist ${version} does not exist"
  exit 1
fi

packages_amd=$(curl -s "http://repo.gardenlinux.io/gardenlinux/dists/${version}/main/binary-amd64/Packages")
packages_arm=$(curl -s "http://repo.gardenlinux.io/gardenlinux/dists/${version}/main/binary-arm64/Packages")
pkg_list=$(for f in features/*/pkg.include; do cat "$f"; echo; done)
while IFS= read -r pkg; do

  # Skip Empty whitespace lines
  if [[ -z "${pkg// }" ]]; then
    continue
  fi

  # Ignore Comments in pkg.include files
  if [[ "${pkg:0:1}" == "#" ]]; then
    continue
  fi

  arch="both"
  # respect architecture annotation
  if grep "^[\[].*" -q <<< "$pkg"; then
    in_var=$pkg
    arch=${in_var#*=}
    arch=${arch%]*}
    pkg=${pkg#*]}
  fi

  case $arch in
    arm64)
      check_pkg "$packages_arm" "$pkg" "arm64"
      ;;

    amd64)
      check_pkg "$packages_amd" "$pkg" "amd64"
      ;;

    both)
      check_pkg "$packages_arm" "$pkg" "arm64"
      check_pkg "$packages_amd" "$pkg" "amd64"
      ;;

    *)
      echo -n "Unknown Architecture $arch"
      ;;
  esac

done < <(echo "$pkg_list")

if [ ${#missing_packages[@]} -eq 0 ]; then
  exit 0
else
  echo "Missing Packages in apt repo ${version}:"
  printf '\t%s\n' "${missing_packages[@]}"
  exit 1
fi
