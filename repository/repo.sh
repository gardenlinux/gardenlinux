#!/usr/bin/env bash

set -euo pipefail
shopt -s extglob
fail=0
PUBLISH="false"
REFRESH="false"
DOWNLOAD="false"
NO_GPG="false"
SET_GPG="false"
listPackage=""
deletePackage=""

usage() {
        echo -e "usage: $0
        --packages-list          Specify the Debian packages list file
	--codename               Specify the codename for the repository (defaults to testing)
	--repository             Specify the repository (defaults to 'deb http://ftp.de.debian.org/debian testing main')
        --download               Download the packages from the debian repository
        --publish                Publish the changes to the repository 
        --refresh                Refresh the repository if files have been added to the pool
	--all                    Download the debian packages, publish them and the sap packages if there are any
	--no-gpg                 Do not use a GPG key 
        --on-the-fly             TODO : generate a repo on the fly 
	--remove		 Remove specific package from the repository
	--describe               Status of package/history
	--list=<package>	 List the package information
	--delete=<package>	 Remove the package from the repository 
	--gpg-key=<key>          Use different GPG key that what is defined in the settings file. Make sure to use with --set-gpg option.
        --set-gpg	         Force a new gpg key to be defined
        -h                       Help usage\n" >&2
}

download_debian() {
	local packagesList=$1
	local repo=$2
	local tmpdir=$(mktemp -d)

	trap 'rm -rf ${tmpdir}' RETURN

	echo "${repo}" > "${tmpdir}/list"
	echo "${repo}" | sed 's/deb /deb-src /' >> "${tmpdir}/list"
	mkdir "$tmpdir/lists"
	mkdir -p "$tmpdir/cache/partial"
	# fix permissions so it can download
	chown _apt "$tmpdir"
	chown _apt "$tmpdir/lists"
	chown _apt "$thisDir/packages/${CODENAME}/main"

	apt-get -o Dir::Etc::SourceList="$tmpdir/list" -o Dir::Etc::SourceParts= -o Dir::State::Lists="${tmpdir}/lists" -o Dir::Cache::Archives="${tmpdir}/cache" update 

	apt-cache -o Dir::Etc::SourceList="$tmpdir/list" -o Dir::Etc::SourceParts= -o Dir::State::Lists="${tmpdir}/lists" -o Dir::Cache::Archives="${tmpdir}/cache" depends $(grep . "${thisDir}/${packagesList}") | awk '$0 ~ /^  Depends: </ {depends=1; next}; /^    / { if (depends == 1) {print $1; next}}; $0 ~ /Depends: / { print $2 }; depends=0' >> "${tmpdir}/packagelistdeps"

	cat "${thisDir}"/"${packagesList}" >> "${tmpdir}"/packagelistdeps

	(cd "${thisDir}/packages/${CODENAME}/main"; apt-get -o Dir::Etc::SourceList="$tmpdir/list" -o Dir::Etc::SourceParts= -o Dir::State::Lists="${tmpdir}/lists" -o Dir::Cache::Archives="${tmpdir}/cache" download $(sort "${tmpdir}/packagelistdeps" | uniq )) 
	#ls -latr ${tmpdir}/cache
	(cd "${thisDir}/packages/${CODENAME}/source"; apt-get -o Dir::Etc::SourceList="$tmpdir/list" -o Dir::Etc::SourceParts= -o Dir::State::Lists="${tmpdir}/lists" -o Dir::Cache::Archives="${tmpdir}/cache" source --download-only $(sort "${tmpdir}/packagelistdeps" | uniq )) 
}

publish() {
	for distro in "${thisDir}"/packages/*; do
		for component in "${distro}"/*; do
			if [[ $(shopt -s nullglob dotglob; f=("${component}"/*); echo ${#f[@]}) -eq 0 ]]; then
				echo "nothing to do for $(basename "${distro}")/$(basename "${component}"), skipping"
				continue
 			fi 
			if [[ $(basename "${component}") == "source" ]]; then
				for dsc in "${component}"/*.dsc; do
					reprepro -s -b "${thisDir}/reprepro" includedsc "$(basename "${distro}")" "${dsc}"
				done
			else
				reprepro -s -C "$(basename "${component}")" -b "${thisDir}/reprepro" includedeb "$(basename "${distro}")" "${component}"/*.deb
			fi
		done
	done	

	# sap packages

	if [[ $(shopt -s nullglob dotglob; f=("${thisDir}/packages_gardenlinux"/*.deb); echo ${#f[@]}) -ne 0 ]]; then
		reprepro -s -C "main" -b "${thisDir}/reprepro" includedeb "${CODENAME}" "${thisDir}/packages_gardenlinux"/!(*@(-dbg_|-dbgsym_)*).deb 
		reprepro -s -C "main" -b "${thisDir}/reprepro" includedeb "${CODENAME}-debug" "${thisDir}/packages_gardenlinux"/*@(-dbg_|-dbgsym_)*.deb 
	else
		echo "no specific gardenlinux packags found, skipping"
 	fi 
	if [[ $(shopt -s nullglob dotglob; f=("${thisDir}/packages_gardenlinux"/*.dsc); echo ${#f[@]}) -ne 0 ]]; then
		for dsc in "${thisDir}/packages_gardenlinux"/*.dsc; do
			reprepro -s -b "${thisDir}/reprepro" includedsc "${CODENAME}" "${dsc}"
		done
	else
		echo "no specific gardenlinux source packages found, skipping"
	fi

	reprepro -s -b "${thisDir}/reprepro" createsymlinks
}

refresh() {
	echo "Refreshing the repository"
	reprepro -b "${thisDir}/reprepro/" export 
}

list() {
	local package=$1
	reprepro  -b "${thisDir}/reprepro/" list "${CODENAME}" "$package" 
}

delete() {
	local package=$1
	reprepro  -b "${thisDir}/reprepro/" remove "${CODENAME}" "$package" 
}

thisDir=$(readlink -f "$(dirname "${BASH_SOURCE[0]}")")
# shellcheck source=./settings
source "${thisDir}/settings"

# reading commandline parameters
while getopts ":h-:" optchar; do
    case "${optchar}" in
        -)
        case "${OPTARG}" in
            packages-list=*)
                PACKAGES_DEBIAN=${OPTARG#*=}
                ;;
            codename=*)
                CODENAME=${OPTARG#*=}
                ;;
            gpg-key=*)
                GPG_KEY=${OPTARG#*=}
                ;;
            repository=*)
                REPOSITORY=${OPTARG#*=}
                ;;
            list=*)
                listPackage=${OPTARG#*=}
                ;;
            delete=*)
                deletePackage=${OPTARG#*=}
                ;;
	    download)
	        DOWNLOAD=true
		;;
            publish)
                PUBLISH=true
		;;
            no-gpg)
                NO_GPG=true
		;;
            set-gpg)
                SET_GPG=true
		;;
            refresh)
                REFRESH=true
		;;
	    all)
		DOWNLOAD=true
		PUBLISH=true
		;;
            *)
                if [ "$OPTERR" = 1 ]; then
                    echo "Unknown option --${OPTARG}" >&2
                    fail=1
                fi
                ;;
        esac
        ;;
        h)
            usage
        exit 0
            ;;
        *)
            echo "Non-option argument: '-${OPTARG}'" >&2
            fail=1
            ;;
    esac
done
[[ ${fail} -eq 1 ]] && usage && exit 1


# signing
if [[ "$NO_GPG" == "true" ]]; then
	echo "Removing the signing key from the repository"
	distributionsTemp="${thisDir}/reprepro/conf/distributions.tmp"
	distributions="${thisDir}/reprepro/conf/distributions"
	timestamp=$(date +%s)
	cp "$distributions" "${distributions}.${timestamp}"
	sed -i '/^SignWith: .*/d' "${thisDir}/reprepro/conf/distributions" 
fi

if [[ "$GPG_KEY" != "no" && "$SET_GPG" == "true" ]]; then
	echo "Adding signing key for the repository"
	distributionsTemp="${thisDir}/reprepro/conf/distributions.tmp"
	distributions="${thisDir}/reprepro/conf/distributions"
	#if ! gpg --list-secret-keys --keyid-format LONG | grep -qw "$GPG_KEY"; then
	#	echo "GPG key not in your keyring, exiting"
	#	exit 1
	#fi
	# backing up, just in case
	timestamp=$(date +%s)
	cp "$distributions" "${distributions}.${timestamp}"
	sed -i '/^SignWith: .*/d' "${distributions}" 
	awk -v RS="" -F'\n' -v OFS="\n" -v s="SignWith: ${GPG_KEY}" '{$1=$1;print $0;print s"\n"}' "$distributions" > "$distributionsTemp" | sed -i '${/^$/d;};' "${distributionsTemp}" && mv ${distributionsTemp} ${distributions}
fi

if [[ ${DOWNLOAD} == "true" ]]; then
	echo "Downloading needed debian packages"
	download_debian "${PACKAGES_DEBIAN}" "${REPOSITORY}" 
fi

if [[ ${PUBLISH} == "true" ]]; then
	echo "Publishing the needed packages"
	publish 
fi

if [[ ${REFRESH} == "true" ]]; then
	refresh
fi


if [[ ! -z "${listPackage}" ]]; then
	list "${listPackage}"
	if log=$(grep "${listPackage}" "${thisDir}/reprepro/logs/gardenlinux.log" | tail); then
		echo "Last 10 lines of logs relating to this package"
		echo "$log"
	fi
fi

if [[ ! -z "${deletePackage}" ]]; then
	delete "${deletePackage}"
fi
