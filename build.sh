#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/bin/.constants.sh" \
	--flags 'no-build,debug,lessram,manual' \
	--flags 'arch:,qemu,features:,suite:,ports' \
	-- \
	'[--no-build] [--lessram] [--debug] [--manual] [--arch=<arch>] [--qemu] <output-dir> <version/timestamp>' \
	'output stretch 2017-05-08T00:00:00Z
--eol output squeeze 2016-03-14T00:00:00Z
--eol --arch i386 output sarge 2016-03-14T00:00:00Z' 

eval "$dgetopt"
build=1
debug=
manual=
lessram=
arch=
qemu=
features=
suite="bullseye"
suiteports=
while true; do
	flag="$1"; shift
	dgetopt-case "$flag"
	case "$flag" in
		--no-build)	build= ;;	# skipping "docker build"
		--lessram)	lessram=1 ;;	# build will no longer uses a ramdisk
		--debug)	debug=1 ;;	# using set -x everywhere
		--manual)	manual=1 ;;	# jumps in the prepared image without executeing
		--arch)		arch="$1"; shift ;; # building the image for arch (if empty build arch running on)
		--qemu) 	qemu=1 ;;	# for using "qemu-debootstrap" and "start-vm"
		--features) 	features="$1"; shift ;; # adding featurelist
		--suite) 	suite="$1"; shift ;; # adding suite
		--ports)        suiteports=1 ;;      # enables "debian-ports" support for suite
		--) break ;;
		*) eusage "unknown flag '$flag'" ;;
	esac
done

outputDir="${1:-}";	shift || eusage 'missing output-dir'
version="$(bin/garden-version --major ${1:-})";	shift || /bin/true

mkdir -p "$outputDir"
outputDir="$(readlink -f "$outputDir")"

envArgs=(
	TZ="UTC"
	LC_ALL="C"
	suite="$suite"
	suiteports="$suiteports"
	debug="$debug"
	manual="$manual"
	qemu="$qemu"
	arch="$arch" 
	features="$features"
	version="$version"
)

securityArgs=( 
	--cap-add SYS_ADMIN	# needed for mounts in image
	--cap-drop SETFCAP
	--privileged		# needed for creating bootable images with losetup and a mounted /dev
)

dockerinfo="$(docker info)"       || eusage "docker not working, check permissions or work with bin/garden-build.sh"
grep -q apparmor <<< $dockerinfo  && securityArgs+=( --security-opt apparmor=unconfined )

# external variable BUILD_IMAGE forces a different buildimage name
buildImage=${BUILD_IMAGE:-"gardenlinux/build-image:$version"}
[ $build ] && docker build -t "$buildImage" "$thisDir"

# using the buildimage in a temporary container with
# build directory mounted in memory (--tmpfs ...) and
# dev mounted via bind so loopback device changes are reflected into the container
dockerArgs="--hostname garden-build
	${securityArgs[*]}
	${envArgs[*]/#/-e }
	--volume ${thisDir}:/opt/gardenlinux
	--mount type=bind,source=/dev,target=/dev"

[ $lessram ] || dockerArgs+=" --tmpfs /tmp:dev,exec,suid,noatime"

if [ $manual ]; then
	echo -e "\n### running in debug mode"
	echo -e "please run -> /opt/gardenlinux/bin/garden-build.sh <- (all configs are set)\n"
	set -x
	docker run $dockerArgs -ti \
		"${buildImage}" \
		/bin/bash
else
	set -x
	docker run $dockerArgs --rm \
		"${buildImage}" \
		/opt/gardenlinux/bin/garden-build.sh | tar -xvC "$outputDir"
fi
