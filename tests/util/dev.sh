# shellcheck shell=bash
# shellcheck disable=SC2154,SC2164
BUILD_DIR="$(realpath "${util_dir}/../.build")"
TESTS_DIR="$(realpath "${util_dir}/../../tests")"

WEBSITINO_BIN_FILE="${BUILD_DIR}/websitino"
WEBSITINO_PID_FILE="${BUILD_DIR}/.websitino.pid"
WEBSITINO_LOG="${BUILD_DIR}/websitino.log"

NOTIFY_CLIENT="${util_dir}/dev/notify_client.py"
NOTIFY_CLIENT_PID_FILE="${BUILD_DIR}/.notify_client.pid"
NOTIFY_CLIENT_LOG="${BUILD_DIR}/notify_client.log"
NOTIFY_CLIENT_VENV="${BUILD_DIR}/.notify_client_venv"

WEBSITINO_VERSION="0.2.8"
DAEMONIZE_VERSION="1.7.8"

WEBSITINO_PORT="8123"
NOTIFY_SERVER_PORT="9999"

DEV_DEBUG=0

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
			_help_dev_macos_dependencies daemonize
		fi
		;;
	*) _help_dev_unsupported_os ;;
	esac
}

build_daemonize_podman() {
	printf "==>\t\tbuilding daemonize in podman...\n"
	cat <<EOF >"${BUILD_DIR}/Containerfile.daemonize"
FROM docker.io/library/ubuntu:16.04
# ^^^ there is no way to have a static build of daemonize
#     (or at least I don't know about it),
#     so we need as old glibc as we can get 
#     to ensure the binary from the container will work on the target system
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

build_websitino() {
	case $(uname -s) in
	Linux)
		build_websitino_podman
		;;
	Darwin)
		if ! brew list ldc >/dev/null 2>&1; then
			_help_dev_macos_dependencies ldc dub
		fi
		if ! brew list dub >/dev/null 2>&1; then
			_help_dev_macos_dependencies dub
		fi

		build_websitino_macos
		;;
	*) _help_dev_unsupported_os ;;
	esac
}

build_websitino_podman() {
	printf "==>\t\tbuilding websitino in podman...\n"
	cat <<EOF >"${BUILD_DIR}/Containerfile.websitino"
FROM alpine:3.23.3
RUN echo "$(date '+%s')" # this is required to invalidate podman cache
RUN apk add gcc musl-dev ldc dub llvm-libunwind-static
RUN dub build -y --verbose --config linux-static websitino@${WEBSITINO_VERSION}
RUN cp -v /root/.dub/packages/websitino/${WEBSITINO_VERSION}/websitino/websitino /output/websitino
EOF
	podman build -f "${BUILD_DIR}/Containerfile.websitino" --volume "${BUILD_DIR}:/output" "${BUILD_DIR}"
	rm -f "${BUILD_DIR}/Containerfile.websitino"
	printf "Done.\n"
}

build_websitino_macos() {
	printf "==>\t\tbuilding websitino..."
	dub build -y --verbose --compiler ldmd2 websitino@${WEBSITINO_VERSION}
	cp -v "$HOME/.dub/packages/websitino/${WEBSITINO_VERSION}/websitino/websitino" "${WEBSITINO_BIN_FILE}"
	printf "Done.\n"
}

start_notify_client() {
	case $(uname -s) in
	Linux)
		_daemonize_bin="${BUILD_DIR}/daemonize"
		;;
	Darwin)
		_daemonize_bin="daemonize"
		;;
	*) _help_dev_unsupported_os ;;
	esac

	printf "==>\t\tstarting notify client..."
	: >"${NOTIFY_CLIENT_LOG}"
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
		-o "${NOTIFY_CLIENT_LOG}" \
		-e "${NOTIFY_CLIENT_LOG}" \
		-p "${NOTIFY_CLIENT_PID_FILE}" \
		"${NOTIFY_CLIENT_VENV}/bin/python" \
		"${NOTIFY_CLIENT}" \
		--server "localhost:${NOTIFY_SERVER_PORT}" \
		-i "${TESTS_DIR}" \
		-e "${TESTS_DIR}/cert/" -e "${TESTS_DIR}/.build/" -e "${TESTS_DIR}/util/"
	printf "Done.\n"
}

stop_notify_client() {
	printf "==>\t\tstopping notify client..."
	if [ -f "${NOTIFY_CLIENT_PID_FILE}" ]; then
		if ! kill -0 "$(cat "${NOTIFY_CLIENT_PID_FILE}")"; then
			rm -f "${NOTIFY_CLIENT_PID_FILE}"
		else
			kill "$(cat "${NOTIFY_CLIENT_PID_FILE}")" && rm -f "${NOTIFY_CLIENT_PID_FILE}"
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

add_qemu_notify_port_forwarding() {
	for idx in "${!qemu_opts[@]}"; do
		case "${qemu_opts[idx]}" in
		*hostfwd*)
			qemu_opts[idx]="${qemu_opts[idx]},hostfwd=tcp::${NOTIFY_SERVER_PORT}-:${NOTIFY_SERVER_PORT}"
			;;
		esac
	done
}

dev_configure_runner() { # path-to-script test-arg1 test-arg2 ... test-argN
	_runner_script="$1"
	shift

	cat >>"$_runner_script" <<EOF
set -e
export PYTHONUNBUFFERED=1
export OPENSSL_MODULES=/usr/lib/\$(uname -m)-linux-gnu/ossl-modules/ 
# ^^^ https://github.com/gardenlinux/gardenlinux/pull/3797

/run/gardenlinux-tests/runtime/\$(uname -m)/bin/python3 -c \
"import os, urllib.request; urllib.request.urlretrieve('http://10.0.2.2:${WEBSITINO_PORT}/util/dev/notify_server.py', '/run/notify_server.py')"

/run/gardenlinux-tests/runtime/\$(uname -m)/bin/python3 \
  /run/notify_server.py \
  http://10.0.2.2:${WEBSITINO_PORT} \
  "${TESTS_DIR}" -- $@
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
  /sbin/nft add rule inet filter input tcp dport ${NOTIFY_SERVER_PORT} ct state new counter accept
fi
/sbin/iptables -A INPUT -p tcp -m tcp --dport ${NOTIFY_SERVER_PORT} -m state --state NEW -j ACCEPT

mkdir -p /run/gardenlinux-tests.{overlay,work}
mount -t overlay overlay \
  -o lowerdir=/run/gardenlinux-tests,upperdir=/run/gardenlinux-tests.overlay,workdir=/run/gardenlinux-tests.work \
  /run/gardenlinux-tests
EOF
}

setup_notify_client() {
	(
		python3 -mvenv "${NOTIFY_CLIENT_VENV}"
		. "${NOTIFY_CLIENT_VENV}/bin/activate"
		pip install watchfiles==1.1.1
	)
}

dev_cleanup() {
	stop_notify_client
	stop_websitino
}

# main entrypoint
dev_setup() { # path-to-script
	_runner_script="$1"

	build_daemonize

	[ -d "${NOTIFY_CLIENT_VENV}" ] || setup_notify_client
	[ -x "${WEBSITINO_BIN_FILE}" ] || build_websitino

	configure_vm_runner_script

	if [ $DEV_DEBUG = 1 ]; then
		printf "==>\t\trunner script contents:\n"
		cat "$_runner_script"
		printf "==>\t\tend of runner script contents.\n"
	fi

	stop_websitino
	start_websitino

	stop_notify_client
	start_notify_client
}

trap "dev_cleanup" ERR EXIT INT
