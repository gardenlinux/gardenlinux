# shellcheck shell=bash
# shellcheck disable=SC2154,SC2164
HOST_OS=$(uname -s)
BUILD_DIR="$(realpath "${util_dir}/../.build")"
TESTS_DIR="$(realpath "${util_dir}/../../tests-ng")"

XNOTIFY_CLIENT_BIN_FILE="${BUILD_DIR}/xnotify__${HOST_OS}"
XNOTIFY_CLIENT_PID_FILE="${BUILD_DIR}/.xnotify.pid"
XNOTIFY_CLIENT_LOG="${BUILD_DIR}/xnotify.log"
XNOTIFY_SERVER_BIN_FILE="${BUILD_DIR}/xnotify__Linux"

WEBSITINO_BIN_FILE="${BUILD_DIR}/websitino"
WEBSITINO_PID_FILE="${BUILD_DIR}/.websitino.pid"
WEBSITINO_LOG="${BUILD_DIR}/websitino.log"

SYNCER_SCRIPT_FILE="${BUILD_DIR}/syncer"

DEV_DEBUG=1

WEBSITINO_VERSION="0.2.8"
DAEMONIZE_VERSION="1.7.8"
XNOTIFY_VERSION="0.3.1"

WEBSITINO_PORT="8123"
XNOTIFY_SERVER_PORT="9999"

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
		if ! brew list daemonize >/dev/null 2>&1; then
			_help_dev_macos_dependencies golang daemonize
		fi
		;;
	*) _help_dev_unsupported_os ;;
	esac
}

build_daemonize_podman() {
	printf "==>\t\tbuilding daemonize in podman...\n"
	cat <<EOF >"${BUILD_DIR}/Containerfile.daemonize"
FROM docker.io/library/ubuntu:16.04
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
		if ! brew list golang >/dev/null 2>&1; then
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
	printf "==>\t\tbuilding xnotify in podman...\n"
	cat <<EOF >"${BUILD_DIR}/Containerfile.xnotify"
FROM docker.io/library/golang:1.20.14
RUN echo "$(date '+%s')" # this is required to invalidate podman cache
RUN go install github.com/AgentCosmic/xnotify@v${XNOTIFY_VERSION}
RUN cp -v "/go/bin/xnotify" /output/xnotify
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

build_websitino() {
	case $(uname -s) in
	Linux)
		build_websitino_podman
		;;
	Darwin)
		if ! brew list dmd >/dev/null 2>&1; then
			_help_dev_macos_dependencies dmd
		fi

		build_websitino_macos
		;;
	*) _help_dev_unsupported_os ;;
	esac
}

build_websitino_podman() {
	printf "==>\t\tbuilding websitino in podman...\n"
	cat <<EOF >"${BUILD_DIR}/Containerfile.websitino"
FROM docker.io/library/debian:trixie
RUN echo "$(date '+%s')" # this is required to invalidate podman cache
RUN apt-get update && apt-get install -y wget
RUN wget https://master.dl.sourceforge.net/project/d-apt/files/d-apt.list -O /etc/apt/sources.list.d/d-apt.list
RUN apt-get update --allow-insecure-repositories
RUN apt-get -y --allow-unauthenticated install --reinstall d-apt-keyring
RUN apt-get update && apt-get install -y dmd-compiler dub
RUN dub build -y --verbose websitino@${WEBSITINO_VERSION}
RUN cp -v /root/.dub/packages/websitino/${WEBSITINO_VERSION}/websitino/websitino /output/websitino
EOF
	podman build -f "${BUILD_DIR}/Containerfile.websitino" --volume "${BUILD_DIR}:/output" "${BUILD_DIR}"
	rm -f "${BUILD_DIR}/Containerfile.websitino"
	printf "Done.\n"
}

build_websitino_macos() {
	printf "==>\t\tbuilding websitino...\n"
	dmd build -y --verbose websitino@${WEBSITINO_VERSION}
	cp -v "$HOME/.dub/packages/websitino/${WEBSITINO_VERSION}/websitino/websitino" "${WEBSITINO_BIN_FILE}"
	printf "Done.\n"
}

extract_tests_runner_script() {
	printf "==>\t\textracting test runner script...\n"
	(
		cd "${BUILD_DIR}"
		tar xzf dist.tar.gz ./run_tests
	)
	printf "Done.\n"
}

start_xnotify_client() {
	case $(uname -s) in
	Linux)
		_daemonize_bin="${BUILD_DIR}/daemonize"
		;;
	Darwin)
		_daemonize_bin="daemonize"
		;;
	*) _help_dev_unsupported_os ;;
	esac

	printf "==>\t\tstarting xnotify client..."
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
	printf "==>\t\tstopping xnotify client..."
	if [ -f "${XNOTIFY_CLIENT_PID_FILE}" ]; then
		if ! kill -0 "$(cat "${XNOTIFY_CLIENT_PID_FILE}")"; then
			rm -f "${XNOTIFY_CLIENT_PID_FILE}"
		else
			kill "$(cat "${XNOTIFY_CLIENT_PID_FILE}")" && rm -f "${XNOTIFY_CLIENT_PID_FILE}"
		fi
	fi
	printf "Done.\n"
}

start_websitino() {
	case $(uname -s) in
	Linux)
		_daemonize_bin="${BUILD_DIR}/daemonize"
		;;
	Darwin)
		_daemonize_bin="daemonize"
		;;
	*) _help_dev_unsupported_os ;;
	esac

	printf "==>\t\tstarting websitino..."
	: >"${WEBSITINO_LOG}"
	# -v : verbose output
	# -a : append to log
	# -o : redirect stdout to a file
	# -e : redirect stderr to a file
	# -p : save PID to a file
	# -c : chdir
	#    --client ":NNNN" : send changes to localhost:NNNN
	#    -i : include path to watch
	#    -e : exclude from watching
	"${_daemonize_bin}" \
		-v \
		-a \
		-o "${WEBSITINO_LOG}" \
		-e "${WEBSITINO_LOG}" \
		-p "${WEBSITINO_PID_FILE}" \
		-c "${TESTS_DIR}" \
		"${WEBSITINO_BIN_FILE}" --verbose --bind 127.0.0.1 --port ${WEBSITINO_PORT} --show-hidden
	printf "Done.\n"
}

stop_websitino() {
	printf "==>\t\tstopping websitino..."
	if [ -f "${WEBSITINO_PID_FILE}" ]; then
		if ! kill -0 "$(cat "${WEBSITINO_PID_FILE}")"; then
			rm -f "${WEBSITINO_PID_FILE}"
		else
			kill "$(cat "${WEBSITINO_PID_FILE}")" && rm -f "${WEBSITINO_PID_FILE}"
		fi
	fi
	printf "Done.\n"
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

add_qemu_syncer_script_passing() {
	qemu_opts+=(-fw_cfg "name=opt/gardenlinux/syncer,file=${SYNCER_SCRIPT_FILE}")
}

dev_configure_runner() { # path-to-script test-arg1 test-arg2 ... test-argN
	_runner_script="$1"
	shift

	cat >>"$_runner_script" <<EOF
set -e
curl "http://10.0.2.2:${WEBSITINO_PORT}/.build/$(basename "${XNOTIFY_SERVER_BIN_FILE}")" -o /run/xnotify
chmod +x /run/xnotify

export PYTHONUNBUFFERED=1
/run/xnotify \
  --listen "0.0.0.0:${XNOTIFY_SERVER_PORT}" \
  --base "/run/gardenlinux-tests/tests" \
  --trigger -- \
  /run/syncer $@ 2>&1
EOF
}

configure_vm_runner_script() {
	_tmpf=$(mktemp /tmp/_dev_runner.XXXXXX)
	sed '/set -e/d; /poweroff/d; s,exec 1>/dev/virtio-ports/test_output,exec 1>/dev/console,' "$_runner_script" \
		>"$_tmpf"
	mv "$_tmpf" "$_runner_script"
	cat >>"$_runner_script" <<EOF
if [ "$DEV_DEBUG" = 1 ]; then
    set -x
fi
if [ -x /sbin/nft ]; then
  /sbin/nft add rule inet filter input tcp dport ${XNOTIFY_SERVER_PORT} ct state new counter accept
fi
/sbin/iptables -A INPUT -p tcp -m tcp --dport ${XNOTIFY_SERVER_PORT} -m state --state NEW -j ACCEPT

mkdir -p /run/gardenlinux-tests.{overlay,work}
mount -t overlay overlay \
  -o lowerdir=/run/gardenlinux-tests,upperdir=/run/gardenlinux-tests.overlay,workdir=/run/gardenlinux-tests.work \
  /run/gardenlinux-tests

cp -v /sys/firmware/qemu_fw_cfg/by_name/opt/gardenlinux/syncer/raw /run/syncer
chmod 0755 /run/syncer
EOF
}

configure_syncer_script() {
	cat >"$SYNCER_SCRIPT_FILE" <<EOF
#!/bin/bash
TEST_RUNNER_ARGS="\$@"
BASEURL="http://10.0.2.2:${WEBSITINO_PORT}/"
TESTS_BASEDIR="/run/gardenlinux-tests/tests"

while IFS= read -r src_filename; do
  abs_src_filename="/\${src_filename}"
  download_filename=\${abs_src_filename#${TESTS_DIR}}
  dst_filename="\${TESTS_BASEDIR}/\${download_filename}"
  curl -o "\$dst_filename" "\${BASEURL}\${download_filename}"
done
/run/gardenlinux-tests/run_tests \$TEST_RUNNER_ARGS
EOF
}

dev_cleanup() {
	stop_xnotify_client
	stop_websitino
}

# main entrypoint
dev_setup() { # path-to-script
	_runner_script="$1"

	build_daemonize

	[ -x "${XNOTIFY_CLIENT_BIN_FILE}" ] || build_xnotify_client
	[ -x "${XNOTIFY_SERVER_BIN_FILE}" ] || build_xnotify_server
	[ -x "${WEBSITINO_BIN_FILE}" ] || build_websitino
	[ -x "${BUILD_DIR}/syncer" ] || configure_syncer_script

	configure_vm_runner_script

	if [ $DEV_DEBUG = 1 ]; then
		printf "==>\t\trunner script contents:\n"
		cat "$_runner_script"
		printf "==>\t\tend of runner script contents.\n"
	fi

	stop_websitino
	start_websitino

	stop_xnotify_client
	start_xnotify_client
}

trap "dev_cleanup" ERR EXIT INT
