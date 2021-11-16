#!/usr/bin/env bash

# constants of the universe
export TZ='UTC' LC_ALL='C'
umask 0002
scriptsDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
featureDir="$scriptsDir/../features"
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
			--usage)	dUsage+="$usagePrefix $self${1:+ $1}"$'\n'
					usagePrefix='      '
					samplePrefix='  eg.:'
					shift
					;;
			--sample)	dUsage+="$samplePrefix $self${1:+ $1}"$'\n'
					samplePrefix='      '
					usagePrefix=$'\n''usage:'
					shift
				;;
			--) break ;;
			*) echo >&2 "error: unexpected $BASH_SOURCE flag '$flag'"; exit 1 ;;
		esac
	done
	local dup=$(sort <<< ${dFlags//,/$'\n'} | uniq -d)
	[ -n "$dup" ] && { echo "error: duplicate in flags definition \"${dup//$'\n'/\" \"}\""; exit 1; }
	dup=$(grep -o . <<< ${dFlagsShort} | sort | uniq -d)
	[ -n "$dup" ] && { echo "error: duplicate in flags-short definition \"${dup//$'\n'/\" \"}\""; exit 1; }

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
		echo >&2 "error: $*"
	fi
	echo >&2
	usage >&2
	exit 1
}

_dgetopt() {
	getopt -n "error" \
		-o "+$dFlagsShort" \
		--long "$dFlags" \
		-- "$@" \
		|| eusage 
}

dgetopt='options="$(_dgetopt "$@")"; eval "set -- $options"; unset options'
dgetopt-case() {
	local flag="$1"; shift

	case "$flag" in
		-h|'-?'|--help)	xusage; exit 0 ;;
		--version)	echo "version: $($scriptsDir/garden-version)"; exit 0 ;;
	esac
}

filter_comment () {
    sed "s/#.*$//;/^$/d;s/^[[:space:]]*//;s/[[:space:]]*$//"
}
#filter_variables () {
#    arch=$arch /usr/bin/envsubst
#}
filter_variables () {
    if [ "${1+defined}" ]; then
	if [ "$1" == "" ]; then
		echo "can't filter the variables, empty arch provided via arg!" 1>&2
		exit 1
	fi
    	arch=$1 /usr/bin/envsubst
    elif [ "${dpkgArch+defined}" ]; then
    	arch=$dpkgArch /usr/bin/envsubst
	if [ "$dpkgArch" == "" ]; then
		echo "can't filter the variables, empty dpkgArch!" 1>&2
		exit 1
	fi
    elif [ "${arch+defined}" ]; then
    	arch=$arch /usr/bin/envsubst
	if [ "$arch" == "" ]; then
		echo "can't filter the variables, empty arch!" 1>&2
		exit 1
	fi
    else
        echo "can't filter the variables, nothing defined!" 1>&2
	exit 1
    fi
}
filter_if() {
    awk -F ']' '
      {
        for(i=1;i<=NF-1;i++)  {
          a=$i
          gsub(/ /,"",a)
          gsub(/[\[\]]/,"",a)
          split(a,arn,"!=")
          if (length(arn) > 1)  {
	    if (arn[1] == arn[2]) {next}
	  }
          else {
            split(a,are,"=")
            if (length(are) > 1) { 
	      if (are[1] != are[2]) {next}
	    }
          }
        }
        gsub(/ /,"",$NF)
        print $NF
      }'
}
norm_features() {
    # remove duplicates without sorting, last entry "wins"
    tac | awk '!seen[$0]++' | tac
}
