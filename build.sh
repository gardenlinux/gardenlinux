#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/bin/.constants.sh" \
	--flags 'skip-build,debug,lessram,manual,skip-tests' \
	--flags 'arch:,features:,disable-features:,suite:,local-pkgs:' \
	--usage '[--skip-build] [--lessram] [--debug] [--manual] [--arch=<arch>] [--skip-tests] [<output-dir>] [<version/timestamp>]' \
	--sample '--features kvm,khost --disable-features _slim .build' \
	--sample '--features metal,_pxe --lessram .build' \
	--help  "Generates a Garden Linux image based on features

<output-dir>	target to store the output artifacts (default: .build)
<version>	which version to build (see bin/garden-version)

--features <element>[,<element>]*	comma separated list of features activated (see features/) (default:base)
--disable-features <element>[,<element>]*	comma separated list of features to deactivate (see features/),
		can only be implicit features another feature pulls in  (default:)
--lessram	build will be no longer in memory (default: off)
--debug		activates basically \`set -x\` everywhere (default: off)
--manual	built will stop in build environment and activate manual mode (debugging) (default:off)
--arch		builds for a specific architecture (default: architecture the build runs on)
--suite		specifies the debian suite to build for e.g. bullseye, potatoe (default: testing)
--skip-tests	deactivating tests (default: off)
--skip-build	do not create the build container BUILD_IMAGE variable would specify an alternative name
"

eval "$dgetopt"
build=1
debug=
manual=
lessram=
arch=
features=
disablefeatures=
tests=1
local_pkgs=
output=".build"
while true; do
	flag="$1"; shift
	dgetopt-case "$flag"
	case "$flag" in
		--skip-build)	build=		;;
		--lessram)	lessram=1	;;
		--debug)	debug=1		;;
		--manual)	manual=1	;;
		--arch)		arch="$1"; 	shift ;;
		--features) 	features="$1";	shift ;;
		--disable-features) 	disablefeatures="$1";shift ;;
		--skip-tests)   tests=0	;;
		--local-pkgs) local_pkgs="$1"; shift ;;
		--) break ;;
		*) eusage "unknown flag '$flag'" ;;
	esac
done

outputDir="${1:-$output}";	shift || /bin/true
version="$(${thisDir}/bin/garden-version ${1:-})";	shift || /bin/true

mkdir -p "$outputDir"
outputDir="$(readlink -f "$outputDir")"

userID=$(id -u)
userGID=$(id -g)
envArgs=(
	TZ="UTC"
	LC_ALL="C"
	suite="bookworm"
	debug=$debug
	manual=$manual
	arch="$arch"
	features="$features"
	disablefeatures="$disablefeatures"
	version="$version"
	tests=$tests
	userID="$userID"
	userGID="$userGID"
)

securityArgs=(
	--cap-add SYS_ADMIN	# needed for unshare in garden-chroot
)

dockerinfo="$(docker info)"       || eusage "docker not working, check permissions or work with bin/garden-build"
grep -q apparmor <<< $dockerinfo  && securityArgs+=( --security-opt apparmor=unconfined )

make --directory=${thisDir}/bin

# external variable BUILD_IMAGE forces a different buildimage name
buildImage=${BUILD_IMAGE:-"gardenlinux/build-image:$version"}
[ $build ] && make --directory=${thisDir}/docker ALTNAME=$buildImage build-image

[ -e ${thisDir}/cert/Kernel.sign.crt ] || make --directory=${thisDir}/cert Kernel.sign.crt
[ -e ${thisDir}/cert/Kernel.sign.key ] || make --directory=${thisDir}/cert Kernel.sign.key

# using the buildimage in a temporary container with
# build directory mounted in memory (--tmpfs ...) and
# dev mounted via bind so loopback device changes are reflected into the container
dockerArgs="--hostname garden-build
	${securityArgs[*]}
	${envArgs[*]/#/-e }
	--volume ${thisDir}:/opt/gardenlinux
	--volume ${outputDir}:/output
	--volume ${thisDir}/cert/Kernel.sign.crt:/kernel.crt
	--volume ${thisDir}/cert/Kernel.sign.key:/kernel.key"

[ $lessram ] || dockerArgs+=" --tmpfs /tmp:dev,exec,suid,noatime"

if [ -n "$local_pkgs" ]; then
	dockerArgs+=" --volume $(realpath "$local_pkgs"):/opt/packages/pool:ro -e PKG_DIR=/opt/packages"
fi

if [ $manual ]; then
	echo -e "\n### running in debug mode"
	echo -e "please run -> /opt/gardenlinux/bin/garden-build <- (all configs are set)\n"
	set -x
	docker run $dockerArgs -ti \
		"${buildImage}" \
		/bin/bash
else
	set -x
	function stop(){
		echo "trapped ctrl-c"
		docker stop -t 0 $1
		wait
		echo "everything stopped..."
		exit 1
	}
	containerName=$(cat /proc/sys/kernel/random/uuid)
	trap 'stop $containerName' INT
	docker run --name $containerName $dockerArgs --rm \
		"${buildImage}" \
		/opt/gardenlinux/bin/garden-build &
	wait %1
fi
