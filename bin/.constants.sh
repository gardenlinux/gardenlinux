#!/usr/bin/env bash

# constants of the universe
export TZ='UTC' LC_ALL='C'
umask 0002
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

options="$(getopt -n "$BASH_SOURCE" -o '+' --long 'flags:,flags-short:,help:,usage:,sample:' -- "$@")"
dFlags='help,version'
dFlagsShort='h?'
dHelp=
dUsage=
__cgetopt() {
	eval "set -- $options" # in a function since otherwise "set" will overwrite the parent script's positional args too
	unset options
	local usagePrefix='usage:'
	local samplePrefix='  eg.:'

	while true; do
		local flag="$1"; shift
		case "$flag" in
			--flags) 	dFlags="${dFlags:+$dFlags,}$1"; shift ;;
			--flags-short)	dFlagsShort="${dFlagsShort}$1"; shift ;;
			--help)		dHelp+="$1"$'\n'; shift ;;
			--usage)
					dUsage+="$usagePrefix $self${1:+ $1}"$'\n'
					usagePrefix='      '
					samplePrefix='  eg.:'
					shift
					;;
			--sample)	
					dUsage+="$samplePrefix $self${1:+ $1}"$'\n'
					samplePrefix='      '
					usagePrefix=$'\n''usage:'
					shift
				;;
			--) break ;;
			*) echo >&2 "error: unexpected $BASH_SOURCE flag '$flag'"; exit 1 ;;
		esac
	done
	local dup=$(sort <<< ${dFlags//,/$'\n'} | uniq -d)
	[ -n "$dup" ] && { echo "error: duplicate flags definition \"${dup//$'\n'/\" \"}\""; exit 1; }

	return 0 
}
__cgetopt

usage() {
	echo -n "${dUsage:+$dUsage$'\n'}"
	echo "$self: gardenlinux build version $($scriptsDir/garden-version)"
}

xusage() {
	echo "$self: gardenlinux build version $($scriptsDir/garden-version)"$'\n'
	echo -n "${dUsage:+$dUsage$'\n'}"
	echo "$dHelp"
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
		-h|'-?'|--help)	xusage; exit 0 ;;
		--version)	echo "version: $($scriptsDir/garden-version)"; exit 0 ;;
	esac
}
