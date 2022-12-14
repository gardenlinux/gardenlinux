#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/bin/.constants.sh" \
	--flags 'skip-build,debug,lessram,manual,skip-tests,debian-mirror,export-aws-access-key' \
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
--debian-mirror	allows usage of native Debian repository (default: off)
--manual	built will stop in build environment and activate manual mode (debugging) (default:off)
--arch		builds for a specific architecture (default: architecture the build runs on)
--suite		specifies the debian suite to build for e.g. bullseye, potatoe (default: testing)
--skip-tests	deactivating tests (default: off)
--tests		test suite to use, available tests are kvm, chroot (default: chroot)
--skip-build	do not create the build container BUILD_IMAGE variable would specify an alternative name
"

eval "$dgetopt"
build=1
debug=
debianMirror=0
manual=
lessram=
arch=$("${thisDir}"/bin/get_arch.sh)
features=
disablefeatures=
commitid="${commitid:-local}"
skip_tests=0
tests="chroot"
local_pkgs=
output=".build"
cert=cert/
aws_access_key=0

# Update all param flags
while true; do
	flag="$1"; shift
	dgetopt-case "$flag"
	case "$flag" in
		--skip-build)			build=		;;
		--lessram)			lessram=1	;;
		--debug)			debug=1		;;
		--debian-mirror)		debianMirror=1	;;
		--manual)			manual=1	;;
		--arch)				arch="$1"; 	shift ;;
		--features)	 		features="$1";	shift ;;
		--disable-features) 		disablefeatures="$1";shift ;;
		--skip-tests)   		skip_tests=1	;;
		--tests)			tests="$1"; shift ;;
		--local-pkgs) 			local_pkgs="$1"; shift ;;
		--cert) 			cert="$1"; shift ;;
		--export-aws-access-key) 	aws_access_key=1 ;;
		--) break ;;
		*) eusage "unknown flag '$flag'" ;;
	esac
done

# Validate checksums
sha256sum -c --ignore-missing checksums.sha256

outputDir="${1:-$output}";	shift || true
version="$("${thisDir}"/bin/garden-version ${1:-})";	shift || true

mkdir -p "$outputDir"
outputDir="$(readlink -f "$outputDir")"

# Set CRE
gardenlinux_build_cre=${GARDENLINUX_BUILD_CRE:-"sudo podman"}

# Skip tests on distroless builds
if [[ "$features" =~ container ]]; then
	skip_tests=1
fi

build_os="$(uname -s)"
# Eval how to generate uuids based on
# the underlying OS
if [ "Darwin" == $build_os ]; then
        uuid_gen="$(/usr/bin/uuidgen)"
else
        uuid_gen="$(cat /proc/sys/kernel/random/uuid)"
fi

userID=$(id -u)
userGID=$(id -g)
envArgs=(
	TZ="UTC"
	LC_ALL="C"
	suite="bookworm"
	debug=$debug
	debianMirror=$debianMirror
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

if [ "$aws_access_key" = 1 ]; then
	for e in AWS_DEFAULT_REGION AWS_REGION AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN; do
		envArgs+=("$e=${!e}")
	done
fi

securityArgs=(
	--cap-add sys_admin	# needed for unshare in garden-chroot
	--cap-add mknod     # needed for debootstrap in garden-init
	--cap-add audit_write	# needed for selinux in makepart
)

dockerinfo="$(${gardenlinux_build_cre} info)"       || eusage "${gardenlinux_build_cre} not working, check permissions or work with bin/garden-build"
grep -q apparmor <<< $dockerinfo  && securityArgs+=( --security-opt apparmor=unconfined )

# external variable BUILD_IMAGE forces a different buildimage name
buildImage=${BUILD_IMAGE:-"gardenlinux/build-image:$version"}
[ $build ] && make --directory="${thisDir}"/container ALTNAME=$buildImage build-image

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

if [ -d .git ] && [ -z "$(git status --porcelain)" ]; then
	commitid_long="$(git rev-parse HEAD)"
	commitid="$(git rev-parse --short HEAD)"
	echo "clean working tree, using $commitid as commit id"
	dockerArgs+=" -e commitid=$commitid -e commitid_long=$commitid_long"
else
	echo 'modified working tree, using "local" instead of commit id'
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
	containerName=$uuid_gen
	trap 'stop $containerName' INT
	${gardenlinux_build_cre} run --name $containerName $dockerArgs --rm \
		"${buildImage}" \
		/opt/gardenlinux/bin/garden-build &
	wait %1

	# append test logs to build logs
	testLog="${outputDir}/$(cat $outputDir/prefix.info).log"
	printf "\nTests\n\n" >> "$testLog"
	exec > >(tee -a "${testLog}") 2> >(tee -a "${testLog}" >&2)

	# Run tests if activated
	if [ ${skip_tests} -eq 0 ] && [[ "${tests}" == *"chroot"* ]]; then
		# Prepare the test container execution
		echo "Creating config file for chroot tests"
		containerName=$uuid_gen
		prefix="$(cat $outputDir/prefix.info)"
		fullfeatures="$(cat $outputDir/fullfeature.info)"
		configDir=$("${thisDir}"/bin/garden-integration-test-config chroot ${prefix} ${fullfeatures} ${outputDir} ${arch})
		dockerArgs=(
			--cap-add sys_admin
			--cap-add mknod
			--cap-add audit_write
			--cap-add net_raw
			--security-opt apparmor=unconfined
		)

		# Run the test container using the chroot platform
		echo "Running pytests in chroot"
		${gardenlinux_build_cre} run --name $containerName "${dockerArgs[@]}" --rm \
			-v "$(pwd)":/gardenlinux -v "${configDir}":/config \
			"gardenlinux/base-test:$version" \
			pytest --iaas=chroot --configfile=/config/config.yaml &

		# Cleanup the test container
		wait %1
		rm -r "${configDir}"
	fi
	if [ ${skip_tests} -eq 0 ] && [[ "${tests}" == *"kvm"* ]]; then
		# Prepare the test container execution
		echo "Creating config file for KVM tests"
		containerName=$uuid_gen
		prefix="$(cat $outputDir/prefix.info)"
		fullfeatures="$(cat $outputDir/fullfeature.info)"
		configDir=$("${thisDir}/bin/garden-integration-test-config" kvm ${prefix} ${fullfeatures} ${outputDir} ${arch})
		dockerArgs=()

		# Check if the host system supports KVM.
		# In this case, add it to the container device list.
		if [ -w "/dev/kvm" ]; then
			dockerArgs+="--device=/dev/kvm"
		fi

		# Run the test container using the KVM platform
		echo "Running pytests in KVM"
		${gardenlinux_build_cre} run --name $containerName "${dockerArgs[@]}" --rm \
			-v /boot/:/boot -v /lib/modules:/lib/modules \
			-v "$(pwd)":/gardenlinux -v "${configDir}":/config \
			"gardenlinux/base-test:$version" \
			pytest --iaas=kvm --configfile=/config/config.yaml &

		# Cleanup the test container
		wait %1
		rm -r "${configDir}"
	fi
fi
