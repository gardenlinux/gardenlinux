#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/bin/.constants.sh" \
	--flags 'skip-build,debug,lessram,manual,skip-tests' \
	--flags 'arch:,features:,disable-features:,suite:,local-pkgs:,tests:,cert:' \
	--usage '[--skip-build] [--lessram] [--debug] [--manual] [--arch=<arch>] [--skip-tests] [--tests=<test>,<test>,...] [<output-dir>] [<version/timestamp>]' \
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
--tests		test suite to use, available tests are unittests, kvm, chroot (default: unittests)
--skip-build	do not create the build container BUILD_IMAGE variable would specify an alternative name
"

eval "$dgetopt"
build=1
debug=
manual=
lessram=
arch=$(${thisDir}/get_arch.sh)
features=
disablefeatures=
commitid="${commitid:-local}"
skip_tests=0
tests="unittests,chroot"
local_pkgs=
output=".build"
cert=cert/
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
		--skip-tests)   skip_tests=1	;;
		--tests)	tests="$1"; shift ;;
		--local-pkgs) local_pkgs="$1"; shift ;;
		--cert) cert="$1"; shift ;;
		--) break ;;
		*) eusage "unknown flag '$flag'" ;;
	esac
done

dpkgArch="${arch:-$(dpkg --print-architecture | awk -F- "{ print \$NF }")}"
outputDir="${1:-$output}";	shift || /bin/true
version="$(${thisDir}/bin/garden-version ${1:-})";	shift || /bin/true

mkdir -p "$outputDir"
outputDir="$(readlink -f "$outputDir")"

gardenlinux_build_cre=${GARDENLINUX_BUILD_CRE:-"sudo podman"}

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
	skip_tests=$skip_tests
	tests="$tests"
	userID="$userID"
	userGID="$userGID"
)

securityArgs=(
	--cap-add sys_admin	# needed for unshare in garden-chroot
	--cap-add mknod     # needed for debootstrap in garden-init
	--cap-add audit_write	# needed for selinux in makepart
)

dockerinfo="$(${gardenlinux_build_cre} info)"       || eusage "${gardenlinux_build_cre} not working, check permissions or work with bin/garden-build"
grep -q apparmor <<< $dockerinfo  && securityArgs+=( --security-opt apparmor=unconfined )

make --directory=${thisDir}/bin

# external variable BUILD_IMAGE forces a different buildimage name
buildImage=${BUILD_IMAGE:-"gardenlinux/build-image:$version"}
[ $build ] && make --directory=${thisDir}/container ALTNAME=$buildImage build-image

# using the buildimage in a temporary container with
# build directory mounted in memory (--tmpfs ...) and
# dev mounted via bind so loopback device changes are reflected into the container
dockerArgs="--hostname garden-build
	${securityArgs[*]}
	${envArgs[*]/#/-e }
	--volume ${thisDir}:/opt/gardenlinux
	--volume ${outputDir}:/output"

[ $lessram ] || dockerArgs+=" --tmpfs /tmp:dev,exec,suid"

if [ -n "$local_pkgs" ]; then
	dockerArgs+=" --volume $(realpath "$local_pkgs"):/opt/packages/pool:ro -e PKG_DIR=/opt/packages"
fi

if [ -n "$cert" ]; then
	dockerArgs+=" --volume $(realpath "$cert"):/cert:ro"
fi

if [ $manual ]; then
	echo -e "\n### running in manual mode"
	echo -e "please run -> /opt/gardenlinux/bin/garden-build <- (all configs are set)\n"
	set -x
	${gardenlinux_build_cre} run $dockerArgs -ti \
		"${buildImage}" \
		/bin/bash
else
	set -x
	function stop(){
		echo "trapped ctrl-c"
		${gardenlinux_build_cre} stop -t 0 $1
		wait
		echo "everything stopped..."
		exit 1
	}
	containerName=$(cat /proc/sys/kernel/random/uuid)
	trap 'stop $containerName' INT
	${gardenlinux_build_cre} run --name $containerName $dockerArgs --rm \
		"${buildImage}" \
		/opt/gardenlinux/bin/garden-build &
	wait %1

	# Run tests if activated
	if [ ${skip_tests} -eq 0 ] && [[ "${tests}" =~ .*"unittests".* ]]; then
		echo "Running tests"
		containerName=$(cat /proc/sys/kernel/random/uuid)
		${gardenlinux_build_cre} run --name $containerName $dockerArgs --rm \
			"${buildImage}" \
			/opt/gardenlinux/bin/garden-test &
		wait %1
	fi
	if [ ${skip_tests} -eq 0 ] && [[ "${tests}" == *"chroot"* ]]; then
		echo "Creating config file for chroot tests"
		containerName=$(cat /proc/sys/kernel/random/uuid)
		prefix="$(${thisDir}/bin/garden-feat --featureDir $featureDir --features "$features" --ignore "$disablefeatures" cname)-$dpkgArch-$version-$commitid"
		fullfeatures="$(${thisDir}/bin/garden-feat --featureDir $featureDir --features "$features" --ignore "$disablefeatures" features)"
		configDir=$(${thisDir}/bin/garden-integration-test-config chroot ${prefix} ${fullfeatures} ${outputDir})
		echo "Running pytests in chroot"
		${gardenlinux_build_cre} run --cap-add sys_admin --cap-add mknod --cap-add audit_write --cap-add net_raw --security-opt apparmor=unconfined \
			--name $containerName --rm -v `pwd`:/gardenlinux -v ${configDir}:/config \
			gardenlinux/base-test:dev \
			pytest --iaas=chroot --configfile=/config/config.yaml &
		wait %1
		rm -r ${configDir}
	fi
	if [ ${skip_tests} -eq 0 ] && [[ "${tests}" == *"kvm"* ]]; then
		echo "Creating config file for KVM tests"
		containerName=$(cat /proc/sys/kernel/random/uuid)
		prefix="$(${thisDir}/bin/garden-feat --featureDir $featureDir --features "$features" --ignore "$disablefeatures" cname)-$dpkgArch-$version-$commitid"
		fullfeatures="$(${thisDir}/bin/garden-feat --featureDir $featureDir --features "$features" --ignore "$disablefeatures" features)"
		configDir=$(${thisDir}/bin/garden-integration-test-config kvm ${prefix} ${fullfeatures} ${outputDir})
		echo "Running pytests in KVM"
		${gardenlinux_build_cre} run --name $containerName --rm -v /boot/:/boot \
			-v /lib/modules:/lib/modules -v `pwd`:/gardenlinux -v ${configDir}:/config \
			gardenlinux/base-test:dev \
			pytest --iaas=kvm --configfile=/config/config.yaml &
		wait %1
		rm -r ${configDir}
	fi
fi
