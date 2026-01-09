# shellcheck shell=bash
# shellcheck disable=SC2154,SC2164
HOST_OS=$(uname -s)
BUILD_DIR="$(realpath "${util_dir}/../.build")"
NFSD_PID_FILE="${BUILD_DIR}/.unfsd.pid"
NFSD_BIN_FILE="${BUILD_DIR}/unfsd__${HOST_OS}"
NFSD_EXPORTS="${BUILD_DIR}/exports"
XNOTIFY_CLIENT_BIN_FILE="${BUILD_DIR}/xnotify__${HOST_OS}"
XNOTIFY_CLIENT_PID_FILE="${BUILD_DIR}/.xnotify.pid"
XNOTIFY_CLIENT_LOG="${BUILD_DIR}/xnotify.log"
XNOTIFY_SERVER_BIN_FILE="${BUILD_DIR}/xnotify__Linux"
TESTS_DIR="$(realpath "${util_dir}/../../tests-ng")"

DAEMONIZE_VERSION="1.7.8"
XNOTIFY_VERSION="0.3.1"
UNFS3_VERSION="0.11.0"

XNOTIFY_SERVER_PORT="9999"
NFSD_SERVER_PORT="4711"

_help_dev_macos_dependencies() { # dep1 dep2 ... depN
	echo "*** We need to install unfsd on your macos system in order to serve files for the dev VM."
	echo "*** However, we noticed that some of the required dependencies are missing."
	echo "*** Please install the dependencies. This is how you can do it with homebrew:"
	echo ""
	echo "brew install ${*}"
	echo ""
	echo "*** Once dependencies are in place, re-run the tests-ng dev suite."
	exit 1
}

_help_dev_unsupported_os() {
	echo "*** You are trying to run tests-ng dev suite on an unsupported OS."
	echo "*** Currently we only support either linux or macos."
	exit 1
}

build_daemonize() {
	case $(uname -s) in
	Linux)
		[ -f "${BUILD_DIR}/daemonize" ] || build_daemonize_podman
		;;
	Darwin)
		if ! which daemonize >/dev/null 2>&1; then
			_help_dev_macos_dependencies golang daemonize
		fi
		;;
	*) _help_dev_unsupported_os ;;
	esac
}

build_daemonize_podman() {
	printf "==>\t\tbuilding daemonize...\n"
	cat <<EOF >"${BUILD_DIR}/Containerfile.daemonize"
FROM ubuntu:16.04 AS build
RUN echo "$(date '+%s')" # this is required to invalidate podman cache
RUN apt-get update && apt-get install -y git make gcc
WORKDIR /build
RUN git clone --branch release-${DAEMONIZE_VERSION} --single-branch https://github.com/bmc/daemonize.git \
  && cd daemonize \
  && ./configure --prefix=/build \
  && make \
  && make install
RUN cp /build/sbin/daemonize /output/daemonize
EOF
	podman build -f "${BUILD_DIR}/Containerfile.daemonize" --volume "${BUILD_DIR}:/output" "${BUILD_DIR}"
	rm -f "${BUILD_DIR}/Containerfile.daemonize"
	printf "Done.\n"
}

build_xnotify_client() {
	case $(uname -s) in
	Linux)
		build_xnotify_podman
		;;
	Darwin)
		brew_prefix=$(brew config | awk -F': ' '/HOMEBREW_PREFIX/ {print $2}')
		if ! which go >/dev/null 2>&1; then
			_help_dev_macos_dependencies golang
		fi

		build_xnotify_macos
		;;
	*) _help_dev_unsupported_os ;;
	esac
}

build_xnotify_server() {
	build_xnotify_podman
}

build_xnotify_podman() {
	printf "==>\t\tbuilding xnotify (linux binary)...\n"
	cat <<EOF >"${BUILD_DIR}/Containerfile.xnotify"
FROM ubuntu:16.04 AS build
RUN echo "$(date '+%s')" # this is required to invalidate podman cache
RUN apt-get update && apt-get install -y wget
WORKDIR /build
RUN wget https://github.com/AgentCosmic/xnotify/releases/download/v${XNOTIFY_VERSION}/xnotify-linux-amd64 \
  && chmod +x xnotify-linux-amd64
RUN cp xnotify-linux-amd64 /output/xnotify
EOF
	podman build -f "${BUILD_DIR}/Containerfile.xnotify" --volume "${BUILD_DIR}:/output" "${BUILD_DIR}"
	mv "${BUILD_DIR}/xnotify" "${XNOTIFY_SERVER_BIN_FILE}"
	rm -f "${BUILD_DIR}/Containerfile.xnotify"
	printf "Done.\n"
}

build_xnotify_macos() {
	(
		printf "==>\t\tbuilding xnotify (macOS binary)...\n"
		go install github.com/AgentCosmic/xnotify@v${XNOTIFY_VERSION}
		cp -v "$(go env GOPATH)/bin/xnotify" "${XNOTIFY_CLIENT_BIN_FILE}"
		printf "Done.\n"
	)
}

build_unfsd_podman() {
	printf "==>\t\tbuilding unfsd...\n"
	cat <<EOF >"${BUILD_DIR}/Containerfile.unfsd"
FROM ubuntu:16.04 AS build
RUN echo "$(date '+%s')" # this is required to invalidate podman cache
RUN apt-get update && apt-get install -y wget tar bzip2 gzip make gcc autoconf sed flex byacc pkg-config
WORKDIR /build
RUN wget https://downloads.sourceforge.net/libtirpc/libtirpc-1.3.7.tar.bz2 \
  && tar xjf libtirpc-1.3.7.tar.bz2 \
  && cd libtirpc-1.3.7 \
  && ./configure --prefix=/build --disable-gssapi --disable-shared \
  && make \
  && make install
RUN wget https://github.com/unfs3/unfs3/releases/download/unfs3-${UNFS3_VERSION}/unfs3-${UNFS3_VERSION}.tar.gz \
  && tar xzf unfs3-${UNFS3_VERSION}.tar.gz \
  && cd unfs3-${UNFS3_VERSION} \
  && ./bootstrap \
  && sed -i 's%^LDFLAGS =.*%LDFLAGS = -L/build/lib -Wl,--whole-archive -ltirpc -lpthread -Wl,--no-whole-archive%' Makefile.in \
  && PKG_CONFIG_PATH=/build/lib/pkgconfig ./configure --prefix=/build \
  && make \
  && make install
RUN cp /build/sbin/unfsd /output/unfsd
EOF
	podman build -f "${BUILD_DIR}/Containerfile.unfsd" --volume "${BUILD_DIR}:/output" "${BUILD_DIR}"
	mv "${BUILD_DIR}/unfsd" "${NFSD_BIN_FILE}"
	rm -f "${BUILD_DIR}/Containerfile.unfsd"
	printf "Done.\n"
}

build_unfsd_macos() {
	(
		printf "==>\t\tbuilding unfsd...\n"
		cd "${BUILD_DIR}"
		rm -f unfs3.tar.gz
		curl -Lo unfs3.tar.gz "https://github.com/unfs3/unfs3/releases/download/unfs3-${UNFS3_VERSION}/unfs3-${UNFS3_VERSION}.tar.gz"
		tar xzf unfs3.tar.gz
		cd unfs3-${UNFS3_VERSION}
		./bootstrap
		./configure --prefix="$PWD/build"
		make
		make install
		cp -v "$PWD/build/sbin/unfsd" "${NFSD_BIN_FILE}"
		printf "Done.\n"
	)
}

build_unfsd() {
	case $(uname -s) in
	Linux) build_unfsd_podman ;;
	Darwin)
		if ! which autoconf >/dev/null 2>&1; then
			_help_dev_macos_dependencies autoconf automake libtool pkgconf libtirpc
		fi
		if ! which automake >/dev/null 2>&1; then
			_help_dev_macos_dependencies autoconf automake libtool pkgconf libtirpc
		fi
		if ! which glibtool >/dev/null 2>&1; then
			_help_dev_macos_dependencies autoconf automake libtool pkgconf libtirpc
		fi
		if ! which pkgconf >/dev/null 2>&1; then
			_help_dev_macos_dependencies autoconf automake libtool pkgconf libtirpc
		fi
		brew_prefix=$(brew config | awk -F': ' '/HOMEBREW_PREFIX/ {print $2}')
		[ -f "${brew_prefix}/lib/libtirpc.dylib" ] || _help_dev_macos_dependencies autoconf automake libtool pkgconf libtirpc

		build_unfsd_macos
		;;
	*) _help_dev_unsupported_os ;;
	esac
}

extract_tests_runtime() {
	printf "==>\t\textracting test runtime...\n"
	(
		cd "${BUILD_DIR}"
		mkdir -p runtime
		tar xzf runtime.tar.gz -C runtime
	)
	printf "Done.\n"
}

extract_tests_runner_script() {
	(
		cd "${BUILD_DIR}"
		tar xzf dist.tar.gz ./run_tests
	)
}

setup_nfs_shares() {
	stop_nfsd

	printf "==>\t\tsetting up NFS shares: "
	cat <<EOF >"${NFSD_EXPORTS}"
"${BUILD_DIR}/runtime" (insecure,ro,no_root_squash)
"${TESTS_DIR}" (insecure,ro,no_root_squash)
EOF
	# -n, -m : NFS and MOUNT services to use non-default ports
	# -e     : path to exports file
	# -p     : do not register with portmap/rpcbind
	# -t     : TCP-only mode
	# -i     : path to PID file
	"${NFSD_BIN_FILE}" \
		-n ${NFSD_SERVER_PORT} -m ${NFSD_SERVER_PORT} \
		-e "${NFSD_EXPORTS}" \
		-p \
		-t \
		-i "${NFSD_PID_FILE}"
	printf "Done.\n"
}

stop_nfsd() {
	if [ -f "${NFSD_PID_FILE}" ]; then
		if ! kill -0 "$(cat "${NFSD_PID_FILE}")"; then
			rm -f "${NFSD_PID_FILE}"
		else
			kill "$(cat "${NFSD_PID_FILE}")" && rm -f "${NFSD_PID_FILE}"
		fi
	fi
}

start_xnotify_client() {
	stop_xnotify_client

	case $(uname -s) in
	Linux)
		_daemonize_bin="${BUILD_DIR}/daemonize"
		;;
	Darwin)
		_daemonize_bin="daemonize"
		;;
	esac

	printf "==>\t\tstarting xnotify client: "
	: >"${XNOTIFY_CLIENT_LOG}"
	# -v : verbose output
	# -a : append to log
	# -o : redirect stdout to a file
	# -e : redirect stderr to a file
	# -p : save PID to a file
	#    --client ":NNNN" : send changes to localhost:NNNN
	#    -i : include path to watch
	#    -e : exclude from watching
	"${_daemonize_bin}" \
		-v \
		-a \
		-o "${XNOTIFY_CLIENT_LOG}" \
		-e "${XNOTIFY_CLIENT_LOG}" \
		-p "${XNOTIFY_CLIENT_PID_FILE}" \
		"${XNOTIFY_CLIENT_BIN_FILE}" \
		--client ":${XNOTIFY_SERVER_PORT}" \
		--verbose \
		-i "${TESTS_DIR}" \
		-e '/cert/' -e '/.build/'
	printf "Done.\n"
}

stop_xnotify_client() {
	if [ -f "${XNOTIFY_CLIENT_PID_FILE}" ]; then
		if ! kill -0 "$(cat "${XNOTIFY_CLIENT_PID_FILE}")"; then
			rm -f "${XNOTIFY_CLIENT_PID_FILE}"
		else
			kill "$(cat "${XNOTIFY_CLIENT_PID_FILE}")" && rm -f "${XNOTIFY_CLIENT_PID_FILE}"
		fi
	fi
}

add_qemu_xnotify_port_forwarding() {
	for idx in "${!qemu_opts[@]}"; do
		case "${qemu_opts[idx]}" in
		*hostfwd*)
			qemu_opts[idx]="${qemu_opts[idx]},hostfwd=tcp::${XNOTIFY_SERVER_PORT}-:${XNOTIFY_SERVER_PORT}"
			;;
		esac
	done
}

dev_setup() { # path-to-script
	_runner_script="$1"

	build_daemonize

	[ -x "${NFSD_BIN_FILE}" ] || build_unfsd
	[ -x "${XNOTIFY_CLIENT_BIN_FILE}" ] || build_xnotify_client
	[ -x "${XNOTIFY_SERVER_BIN_FILE}" ] || build_xnotify_server
	[ -d "${BUILD_DIR}/runtime" ] || extract_tests_runtime
	[ -x "${BUILD_DIR}/run_tests" ] || extract_tests_runner_script

	cp -v "${BUILD_DIR}/run_tests" "${BUILD_DIR}/runtime/"
	cp -v "${XNOTIFY_SERVER_BIN_FILE}" "${BUILD_DIR}/runtime/"

	setup_nfs_shares
	start_xnotify_client

	_tmpf=$(mktemp /tmp/_dev_runner.XXXXXX)
	sed '/set -e/d; /mount/d; /poweroff/d; s,exec 1>/dev/virtio-ports/test_output,exec 1>/dev/console,' "$_runner_script" \
		>"$_tmpf"
	mv "$_tmpf" "$_runner_script"
	cat >>"$_runner_script" <<EOF
if [ ! -f /etc/default/nfs-common ]; then
  mv /sbin/update-initramfs{,.bak}
  apt-get install -y nfs-common
  chmod u-s /sbin/mount.nfs
  mv /sbin/update-initramfs{.bak,}
fi

if ! which strace > /dev/null 2>&1; then
  apt-get install -y strace
fi

iptables -A INPUT -p tcp -m tcp --dport ${XNOTIFY_SERVER_PORT} -m state --state NEW -j ACCEPT

mkdir -p /run/gardenlinux-tests/{runtime,tests}
mount -vvvv -o port=${NFSD_SERVER_PORT},mountport=${NFSD_SERVER_PORT},mountvers=3,nfsvers=3,nolock,tcp 10.0.2.2:${BUILD_DIR}/runtime /run/gardenlinux-tests/runtime
mount -vvvv -o port=${NFSD_SERVER_PORT},mountport=${NFSD_SERVER_PORT},mountvers=3,nfsvers=3,nolock,tcp 10.0.2.2:${TESTS_DIR} /run/gardenlinux-tests/tests
EOF
}

dev_configure_runner() { # path-to-script test-arg1 test-arg2 ... test-argN
	_runner_script="$1"
	shift

	cat >>"$_runner_script" <<EOF
cp /run/gardenlinux-tests/runtime/run_tests /run/gardenlinux-tests/
cp "/run/gardenlinux-tests/runtime/$(basename "${XNOTIFY_SERVER_BIN_FILE}")" /run/gardenlinux-tests/xnotify
export PYTHONUNBUFFERED=1
./xnotify \
  --listen "0.0.0.0:${XNOTIFY_SERVER_PORT}" \
  --base "/run/gardenlinux-tests/tests" \
  --trigger -- \
  /run/gardenlinux-tests/run_tests $@ 2>&1
EOF
}

dev_cleanup() {
	stop_nfsd
	stop_xnotify_client
}

trap "dev_cleanup" ERR EXIT INT
