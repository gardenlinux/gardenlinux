#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/scripts/.constants.sh" \
	--flags 'no-build,codename-copy' \
	--flags 'eol,ports,arch:,qemu,features:' \
	-- \
	'[--no-build] [--codename-copy] [--eol] [--ports] [--arch=<arch>] [--qemu] <output-dir> <suite> <timestamp>' \
	'output stretch 2017-05-08T00:00:00Z
--codename-copy output stable 2017-05-08T00:00:00Z
--eol output squeeze 2016-03-14T00:00:00Z
--eol --arch i386 output sarge 2016-03-14T00:00:00Z' \

eval "$dgetopt"
build=1
eol=
ports=
arch=
qemu=
features=
while true; do
	flag="$1"; shift
	dgetopt-case "$flag"
	case "$flag" in
		--no-build) build= ;; # for skipping "docker build"
		--eol) eol=1 ;; # for using "archive.debian.org"
		--ports) ports=1 ;; # for using "debian-ports"
		--arch) arch="$1"; shift ;; # for adding "--arch" to debuerreotype-init
		--qemu) qemu=1 ;; # for using "qemu-debootstrap"
		--features) features="$1"; shift ;; # adding features
		--) break ;;
		*) eusage "unknown flag '$flag'" ;;
	esac
done

outputDir="${1:-}"; shift || eusage 'missing output-dir'
suite="${1:-}"; shift || eusage 'missing suite'
timestamp="${1:-}"; shift || eusage 'missing timestamp'

mkdir -p "$outputDir"
outputDir="$(readlink -f "$outputDir")"

securityArgs=(
	--cap-add SYS_ADMIN
	--cap-drop SETFCAP
)
if docker info | grep -q apparmor; then
	# AppArmor blocks mount :)
	securityArgs+=(
		--security-opt apparmor=unconfined
	)
fi

if [ "$suite" = 'potato' ]; then
	# --debian-eol potato wants to run "chroot ... mount ... /proc" which gets blocked (i386, ancient binaries, blah blah blah)
	securityArgs+=(
		--security-opt seccomp=unconfined
	)
fi
#for image creation
securityArgs+=( --privileged )

ver="$("$thisDir/scripts/debuerreotype-version")"
ver="${ver%% *}"
dockerImage="debuerreotype/debuerreotype:$ver"
[ -z "$build" ] || docker build -t "$dockerImage" "$thisDir"
if [ -n "$qemu" ]; then
	[ -z "$build" ] || docker build -t "$dockerImage-qemu" - <<-EODF
		FROM $dockerImage
		RUN apt-get update && apt-get install -y --no-install-recommends qemu-user-static && rm -rf /var/lib/apt/lists/*
	EODF
	dockerImage="$dockerImage-qemu"
fi

set -x

docker run \
	--rm \
	"${securityArgs[@]}" \
	--tmpfs /tmp:dev,exec,suid,noatime \
	--mount type=bind,source=/dev,target=/dev \
	-w /tmp \
	-e suite="$suite" \
	-e timestamp="$timestamp" \
	-e eol="$eol" -e ports="$ports" -e arch="$arch" -e qemu="$qemu" -e features="$features" \
	-e TZ='UTC' -e LC_ALL='C' \
	--hostname debuerreotype \
	"$dockerImage" \
	/opt/debuerreotype/scripts/build.sh | tar -xvC "$outputDir"
