#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/bin/.constants.sh" \
	--flags 'no-build,debug' \
	--flags 'eol,ports,arch:,qemu,features:' \
	-- \
	'[--no-build] [--debug] [--eol] [--ports] [--arch=<arch>] [--qemu] <output-dir> <suite> <timestamp>' \
	'output stretch 2017-05-08T00:00:00Z
--eol output squeeze 2016-03-14T00:00:00Z
--eol --arch i386 output sarge 2016-03-14T00:00:00Z' 

eval "$dgetopt"
build=1
debug=
eol=
ports=
arch=
qemu=
features=
while true; do
	flag="$1"; shift
	dgetopt-case "$flag"
	case "$flag" in
		--no-build) build= ;;	# for skipping "docker build"
		--debug) debug=1 ;;	# for jumping in the prepared image"
		--eol) eol=1 ;;		# for using "archive.debian.org"
		--ports) ports=1 ;;	# for using "debian-ports"
		--arch) arch="$1"; shift ;; # for adding "--arch" to debuerreotype-init
		--qemu) qemu=1 ;;	# for using "qemu-debootstrap"
		--features) features="$1"; shift ;; # adding features
		--) break ;;
		*) eusage "unknown flag '$flag'" ;;
	esac
done

outputDir="${1:-}";	shift || eusage 'missing output-dir'
suite="${1:-}";		shift || eusage 'missing suite'
timestamp="${1:-}";	shift || eusage 'missing timestamp'

mkdir -p "$outputDir"
outputDir="$(readlink -f "$outputDir")"

envArgs=(
	TZ="UTC"
	LC_ALL="C"
	suite="$suite"
	debug="$debug"
	qemu="$qemu"
	eol="$eol" 
	ports="$ports"
	arch="$arch" 
	features="$features"
	timestamp="$timestamp"
)

securityArgs=( 
	--cap-add SYS_ADMIN	# needed for mounts in image
	--cap-drop SETFCAP
	--privileged		# needed for creating bootable images with losetup and a mounted /dev
)

if docker info | grep -q apparmor; then
	# AppArmor blocks mount :)
	securityArgs+=( --security-opt apparmor=unconfined )
fi

if [ "$suite" = 'potato' ]; then
	# --debian-eol potato wants to run "chroot ... mount ... /proc" which gets blocked (i386, ancient binaries, blah blah blah)
	securityArgs+=( --security-opt seccomp=unconfined )
fi

ver="$("$thisDir/bin/debuerreotype-version")"
ver="${ver%% *}"

# external variable BUILD_IMAGE forces a different buildimage name
buildImage=${BUILD_IMAGE:-"debuerreotype/debuerreotype:$ver"}
[ -z "$build" ] || docker build -t "$buildImage" "$thisDir"

# using the buildimage in a temporary container with
# build directory mounted in memory (--tmpfs ...) and
# dev mounted via bind so loopback device changes are reflected into the container
dockerArgs="--hostname garden-build
	${securityArgs[@]}
	${envArgs[*]/#/-e }
	--tmpfs /tmp:dev,exec,suid,noatime
	--mount type=bind,source=/dev,target=/dev"

if [ $debug ]; then
	echo
	echo "### running in debug mode"
	echo "please run -> /opt/debuerreotype/bin/garden-build.sh <-"
	echo
	set -x
	docker run $dockerArgs -ti \
		"${buildImage}" \
		/bin/bash
else
	set -x
	docker run $dockerArgs --rm \
		"${buildImage}" \
		/opt/debuerreotype/bin/garden-build.sh | tar -xvC "$outputDir"
fi
