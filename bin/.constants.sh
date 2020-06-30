#!/usr/bin/env bash

# constants of the universe
export TZ='UTC' LC_ALL='C'
umask 0002
#thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
scriptsDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
self="$(basename "$0")"

#getFeatures() {
#	featureDir="$thisDir/../features"
#	features="$(echo $1 | tr "," "\n")"
#
#	if [ "$1" = "full" ]; then
#		features=($(ls $featureDir | grep -v '^_' | grep -v '.dpkg-'))
#	else
#		IFS=', ' read -r -a features <<< "$1"
#
#	i=0
#	processed=
#	exclude=
#	while [ i -lt ${#feature[@]} ];  do
#		i=$(echo "$features" | head -n1)
#
#		[[ " ${array[@]} " =~ " $i " ]] && continue
#		processsed+=( $i )
#
#		[ ! -d $featureDir/$i] && continue
#
#		[ -s $featureDir/$i/feature.include ] && for i in $(cat $featureDir/$i/include); do include+=( $i ); done
#		[ -s $featureDir/$i/feature.exclude ] && for i in $(cat $featureDir/$i/exclude); do include+=( $i ); done
#	done
#}

options="$(getopt -n "$BASH_SOURCE" -o '+' --long 'flags:,flags-short:' -- "$@")"
dFlags='help,version'
dFlagsShort='h?'
usageStr=
__cgetopt() {
	eval "set -- $options" # in a function since otherwise "set" will overwrite the parent script's positional args too
	unset options

	while true; do
		local flag="$1"; shift
		case "$flag" in
			--flags) dFlags="${dFlags:+$dFlags,}$1"; shift ;;
			--flags-short) dFlagsShort="${dFlagsShort}$1"; shift ;;
			--) break ;;
			*) echo >&2 "error: unexpected $BASH_SOURCE flag '$flag'"; exit 1 ;;
		esac
	done

	while [ "$#" -gt 0 ]; do
		local IFS=$'\n'
		local usagePrefix='usage:' usageLine= linebreak=
		for usageLine in $1; do
			usageStr+="$usagePrefix $self${usageLine:+ $usageLine}"$'\n'
			usagePrefix='      '
			linebreak=1
		done
		usagePrefix='   ie:'
		for usageLine in $2; do
			usageStr+="$usagePrefix $self${usageLine:+ $usageLine}"$'\n'
			usagePrefix='      '
			linebreak=1
		done
		[ $linebreak ] && usageStr+=$'\n'
		shift 2
	done
}
__cgetopt


usage() {
	echo -n "$usageStr"

	local v="$($scriptsDir/garden-version)"
	echo "$self: gardenlinux build version $v"
}
eusage() {
	if [ "$#" -gt 0 ]; then
		if [ "$1" == "-n" ]; then
			echo >&2 ""
		else
			echo >&2 "error: $*"$'\n'
		fi
	fi
	usage >&2
	exit 1
}
_dgetopt() {
	getopt -n "error" \
		-o "+$dFlagsShort" \
		--long "$dFlags" \
		-- "$@" \
		|| eusage -n
}
dgetopt='options="$(_dgetopt "$@")"; eval "set -- $options"; unset options'
dgetopt-case() {
	local flag="$1"; shift

	case "$flag" in
		-h|'-?'|--help) usage; exit 0 ;;
		--version) echo "version: $($scriptsDir/garden-version)" ;;
	esac
}
