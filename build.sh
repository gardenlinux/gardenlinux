#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/bin/.constants.sh" \
	--flags 'skip-build,debug,lessram,manual,skip-tests' \
	--flags 'arch:,features:,disable-features:,suite:,local-pkgs:,tests:' \
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
--tests		test suite to use, available tests are unittests, kvm, chroot (default: unittest)
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
dpkgArch="${arch:-$(dpkg --print-architecture | awk -F- "{ print \$NF }")}"
skip_tests=1
tests="unittests"
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
		--skip-tests)   skip_tests=0	;;
		--tests)	tests="$1"; shift ;;
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

dockerinfo="$(sudo podman info)"       || eusage "sudo podman not working, check permissions or work with bin/garden-build"
grep -q apparmor <<< $dockerinfo  && securityArgs+=( --security-opt apparmor=unconfined )

make --directory=${thisDir}/bin

# external variable BUILD_IMAGE forces a different buildimage name
buildImage=${BUILD_IMAGE:-"gardenlinux/build-image:$version"}
[ $build ] && make --directory=${thisDir}/container ALTNAME=$buildImage build-image

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

[ $lessram ] || dockerArgs+=" --tmpfs /tmp:dev,exec,suid"

if [ -n "$local_pkgs" ]; then
	dockerArgs+=" --volume $(realpath "$local_pkgs"):/opt/packages/pool:ro -e PKG_DIR=/opt/packages"
fi

if [ $manual ]; then
	echo -e "\n### running in manual mode"
	echo -e "please run -> /opt/gardenlinux/bin/garden-build <- (all configs are set)\n"
	set -x
	sudo podman run $dockerArgs -ti \
		"${buildImage}" \
		/bin/bash
else
	set -x
	function stop(){
		echo "trapped ctrl-c"
		sudo podman stop -t 0 $1
		wait
		echo "everything stopped..."
		exit 1
	}
	containerName=$(cat /proc/sys/kernel/random/uuid)
	trap 'stop $containerName' INT
	sudo podman run --name $containerName $dockerArgs --rm \
		"${buildImage}" \
		/opt/gardenlinux/bin/garden-build &
	wait %1

	# Run tests if activated
	if [ ${skip_tests} -eq 1 ] && [[ "${tests}" =~ .*"unittests".* ]]; then
		echo "Running tests"
		containerName=$(cat /proc/sys/kernel/random/uuid)
		sudo podman run --name $containerName $dockerArgs --rm \
			"${buildImage}" \
			/opt/gardenlinux/bin/garden-test &
		wait %1
	fi
	if [ ${skip_tests} -eq 1 ] && [[ "${tests}" == *chroot* ]]; then
		echo "Creating config file for chroot tests"
		containerName=$(cat /proc/sys/kernel/random/uuid)
		prefix="$(${thisDir}/bin/garden-feat --featureDir $featureDir --features "$features" --ignore "$disablefeatures" cname)-$arch-$version-$commitid"
		mkdir -p ${thisDir}/config
		cat > ${thisDir}/config/${containerName}.yaml << EOF
chroot:
    # Path to a final artifact. Represents the .tar.xz archive image file (required)
    image: /gardenlinux/${outputDir##*/}/${prefix}.tar.xz

    # IP or hostname of target machine (required)
    # Default: 127.0.0.1
    ip: 127.0.0.1

    # port for remote connection (required)
    # Default: 2223
    port: 2222

    # SSH configuration (required)
    ssh:
        # Defines path where to look for a given key
        # or to save the new generated one. Take care
        # that you do NOT overwrite your key. (required)
        ssh_key_filepath: /tmp/ssh_priv_key

        # Defines the user for SSH login (required)
        # Default: root
        user: root
EOF
		echo "Running pytests in chroot"
		docker run --cap-add SYS_ADMIN --security-opt apparmor=unconfined \
			--name $containerName --rm -v `pwd`:/gardenlinux \
			gardenlinux/integration-test:dev \
			pytest --iaas=chroot --configfile=/gardenlinux/config/${containerName}.yaml -k 'test_blacklist' &
		wait %1
		rm config/${containerName}.yaml
	fi
	if [ ${skip_tests} -eq 1 ] && [[ "${tests}" == *kvm* ]]; then
		echo "Creating config file for KVM tests"
		containerName=$(cat /proc/sys/kernel/random/uuid)
		prefix="$(${thisDir}/bin/garden-feat --featureDir $featureDir --features "$features" --ignore "$disablefeatures" cname)-$arch-$version-$commitid"
		mkdir -p ${thisDir}/config
		cat > ${thisDir}/config/${containerName}.yaml << EOF
kvm:
    # Path to a final artifact. Represents the .raw image file (required)
    image: /gardenlinux/${outputDir##*/}/${prefix}.raw

    # IP or hostname of target machine (optional)
    # Default: 127.0.0.1
    #ip: 127.0.0.1

    # port for remote connection (required)
    # Default: 2223
    port: 2223

    # Keep machine running after performing tests
    # for further debugging (optional)
    # Default: false
    #keep_running: false

    # Architecture to boot (optional)
    # Default: amd64
    arch: ${dpkgArch}

    # SSH configuration (required)
    ssh:
        # Defines if a new SSH key should be generated (optional)
        # Default: true
        ssh_key_generate: true

        # Defines path where to look for a given key
        # or to save the new generated one. Take care
        # that you do NOT overwrite your key. (required)
        ssh_key_filepath: /tmp/ssh_priv_key

        # Defines if a passphrase for a given key is needed (optional)
        #passphrase: xxyyzz

        # Defines the user for SSH login (required)
        # Default: root
        user: root
EOF
		echo "Running pytests in KVM"
		docker run --name $containerName --rm -v /boot/:/boot \
			-v /lib/modules:/lib/modules -v `pwd`:/gardenlinux  \
			gardenlinux/integration-test:dev \
			pytest --iaas=kvm --configfile=/gardenlinux/config/${containerName}.yaml -k 'test_blacklist' &
		wait %1
		rm config/${containerName}.yaml
	fi
fi
