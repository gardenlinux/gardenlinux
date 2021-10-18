#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/.constants.sh" \
	--flags 'no-build,debug,skip-tests,suite:,gardenversion:,timestamp:' \
	--flags 'ports,arch:,qemu,features:,commitid:,userid:,usergid:' \
	--flags 'suffix:,prefix:' \
	--

export PATH="${thisDir}:${PATH}"
export REPO_ROOT="$(readlink -f "${thisDir}/..")"

commitid="local"
eval "$dgetopt"
while true; do
	flag="$1"; shift
	dgetopt-case "$flag"
	case "$flag" in
		--debug) debug=1 ;;	# for jumping in the prepared image"
		--ports) ports=1 ;;	# for using "debian-ports"
		--arch) arch="$1"; shift ;; # for adding "--arch" to garden-init
		--qemu) qemu=1 ;;	# for using "qemu-debootstrap"
		--features) features="$1"; shift ;; # adding features
		--suite) suite="$1"; shift ;; # suite is a parameter this time
		--gardenversion|--timestamp) version="$1"; shift ;; # timestamp is a parameter this time
		--suffix) suffix="$1"; shift ;; # target name prefix
		--prefix) prefix="$1"; shift ;; # target name suffix
		--commitid) commitid="$1"; shift ;; # build commit hash
		--skip-tests) notests=1 shift ;; # skip tests
		--userid) userID="$1" shift ;;
		--usergid) userGID="$1" shift ;;
		--) break ;;
		*) eusage "unknown flag '$flag'" ;;
	esac
done

if [ ${debug:-} ]; then
	set -x
fi

userID="${userID:-$(id -u)}";
userGID="${userGID:-$(id -g)}";
epoch="$(garden-version --epoch "$version")"
serial="$(garden-version --date "$version")"
dpkgArch="${arch:-$(dpkg --print-architecture | awk -F- "{ print \$NF }")}"

debuerreotypeScriptsDir="$(dirname "$(readlink -f "$(which garden-init)")")"
featureDir="$debuerreotypeScriptsDir/../features"

snapshotUrl="$("$debuerreotypeScriptsDir/.snapshot-url.sh" "@$epoch")/dists/$suite/Release"
codename=$(wget -qO - $snapshotUrl | awk -F: '$1 == "Codename" { print $2 }' | tr -d ' ')

if [ -z "${prefix+x}" ]; then
  prefix="/$serial/$dpkgArch/$codename"
fi

exportDir="output"
outputDir="$exportDir$prefix"

#TODO: clean this up and use volumeDir as outputDir when lessram is used
if [ "${OUTPUT_DIR+defined}" ]; then
	outputDir="${OUTPUT_DIR}${prefix}"
	buildLog="${outputDir}/build.log"
	mkdir -p "${outputDir}"
	touch "${buildLog}"
else
	volumeDir="/output$prefix"
	buildLog="${volumeDir}/build.log"
	mkdir -p "${volumeDir}"

	volDirOwn="$volumeDir"
	while [ $(dirname "${volDirOwn}") != "/" ]; do
		chown "${userID}":"${userGID}" "${volDirOwn}"
		volDirOwn=$(dirname "${volDirOwn}")
	done
	touch "${buildLog}"
	chown "${userID}":"${userGID}" "${buildLog}"
fi

echo > "${buildLog}"
exec > >(tee -a "${buildLog}") 2> >(tee -a "${buildLog}" >&2)

touch_epoch() {
	while [ "$#" -gt 0 ]; do
		local f="$1"; shift
		touch --no-dereference --date="@$epoch" "$f"
	done
}


for archive in "" security; do
	snapshotUrlFile="$outputDir/snapshot-url${archive:+-${archive}}"
	if [ -n "${ports:-}" ] && [ -z "${archive:-}" ]; then
		archive="ports"
	fi
	snapshotUrl="$("$debuerreotypeScriptsDir/.snapshot-url.sh" "@$epoch" "${archive:+debian-${archive}}")"
	mkdir -p "$(dirname "$snapshotUrlFile")"
	echo "$snapshotUrl" > "$snapshotUrlFile"
	touch_epoch "$snapshotUrlFile"
done

export GNUPGHOME="$(mktemp -d)"
keyring="$GNUPGHOME/debian-archive-$suite-keyring.gpg"
if [ "$suite" = potato ]; then
	# src:debian-archive-keyring was created in 2006, thus does not include a key for potato
	gpg --batch --no-default-keyring --keyring "$keyring" \
		--keyserver ha.pool.sks-keyservers.net \
		--recv-keys 8FD47FF1AA9372C37043DC28AA7DEB7B722F1AED
else
	# check against all releases (ie, combine both "debian-archive-keyring.gpg" and "debian-archive-removed-keys.gpg"), since we cannot really know whether the target release became EOL later than the snapshot date we are targeting
	gpg --batch --no-default-keyring --keyring "$keyring" --import \
		/usr/share/keyrings/debian-archive-keyring.gpg \
		/usr/share/keyrings/debian-archive-removed-keys.gpg

	if [ -n "${ports:-}" ]; then
		gpg --batch --no-default-keyring --keyring "$keyring" --import \
			/usr/share/keyrings/debian-ports-archive-keyring.gpg
	fi
fi

snapshotUrl="$(< "$outputDir/snapshot-url")"
mkdir -p "$outputDir"
if wget -O "$outputDir/InRelease" "$snapshotUrl/dists/$suite/InRelease"; then
	gpgv \
		--keyring "$keyring" \
		--output "$outputDir/Release" \
		"$outputDir/InRelease"
else
	wget -O "$outputDir/Release.gpg" "$snapshotUrl/dists/$suite/Release.gpg"
	wget -O "$outputDir/Release" "$snapshotUrl/dists/$suite/Release"
	gpgv \
		--keyring "$keyring" \
		"$outputDir/Release.gpg" \
		"$outputDir/Release"
fi

{
	initArgs=( --arch="$dpkgArch" )
	initArgs+=( --debian )
	if [ -n "${ports-}" ]; then
		initArgs+=(
			--debian-ports
			--include=debian-ports-archive-keyring
		)
	fi
	initArgs+=( --keyring "$keyring" )

	[ -n "$features" ] && initArgs+=( --features "$features" )

	# disable merged-usr (for now?) due to the following compelling arguments:
	#  - https://bugs.debian.org/src:usrmerge ("dpkg-query" breaks, etc)
	#  - https://bugs.debian.org/914208 ("buildd" variant disables merged-usr still)
	#  - https://github.com/debuerreotype/docker-debian-artifacts/issues/60#issuecomment-461426406
	initArgs+=( --no-merged-usr )

	if [ -n "${qemu:-}" ]; then
		initArgs+=( --debootstrap="qemu-debootstrap" )
	fi

	garden-init "${initArgs[@]}" rootfs "$suite" "@$epoch"

	[ -n "$features" ] && configArgs+=( --features "$features" )

	# TODO fix for the pipelines, paths probably won't match
	touch rootfs/etc/gl-sign.crt rootfs/etc/gl-sign.key
	mount --bind /kernel.crt rootfs/etc/gl-sign.crt
	mount --bind /kernel.key rootfs/etc/gl-sign.key
	garden-config "${configArgs[@]}" rootfs
	umount rootfs/etc/gl-sign.crt rootfs/etc/gl-sign.key
	rm -f rootfs/etc/gl-sign.crt rootfs/etc/gl-sign.key
	#garden-apt-get rootfs update -qq
	#garden-apt-get rootfs dist-upgrade -yqq

	aptVersion="$("$debuerreotypeScriptsDir/.apt-version.sh" rootfs)"

	# make a couple copies of rootfs so we can create other variants
	#for variant in slim sbuild; do
	#	mkdir "rootfs-$variant"
	#	tar -cC rootfs . | tar -xC "rootfs-$variant"
	#done

	garden-slimify rootfs

	sourcesListArgs=()
	[ -z "${ports:-}" ] || sourcesListArgs+=( --ports )

	#Brand it
	sed -i "s/^PRETTY_NAME=.*$/PRETTY_NAME=\"Garden Linux $(garden-version)\"/g" rootfs/etc/os-release
	sed -i "s/^HOME_URL=.*$/HOME_URL=\"https:\/\/gardenlinux.io\/\"/g" rootfs/etc/os-release
	sed -i "s/^SUPPORT_URL=.*$/SUPPORT_URL=\"https:\/\/github.com\/gardenlinux\/gardenlinux\"/g" rootfs/etc/os-release
	sed -i "s/^BUG_REPORT_URL=.*$/BUG_REPORT_URL=\"https:\/\/github.com\/gardenlinux\/gardenlinux\/issues\"/g" rootfs/etc/os-release
	echo "GARDENLINUX_FEATURES=$(echo base,$features | tr "," "\n" | norm_features | paste -d"," -s)" >> rootfs/etc/os-release
	echo "GARDENLINUX_VERSION=$($debuerreotypeScriptsDir/garden-version)" >> rootfs/etc/os-release
	echo "GARDENLINUX_COMMIT_ID=$commitid" >> rootfs/etc/os-release
	echo "VERSION_CODENAME=$suite" >> rootfs/etc/os-release
	if [ -f rootfs/etc/update-motd.d/05-logo ]; then
		sed -i "s/@VERSION@/$(garden-version)/" rootfs/etc/update-motd.d/05-logo
	fi

	create_artifacts() {
		local targetBase="$1"; shift
		local rootfs="$1"; shift
		local suite="$1"; shift
		local variant="$1"; shift

		# make a copy of the snapshot-facing sources.list file before we overwrite it
		cp "$rootfs/etc/apt/sources.list" "$targetBase.sources-list-snapshot"
		touch_epoch "$targetBase.sources-list-snapshot"

		local tarArgs=()
		if [ -n "${qemu:-}" ]; then
			tarArgs+=( --exclude="./usr/bin/qemu-*-static" )
		fi

		tarArgs+=( --include-dev )

		if [ "$variant" != "sbuild" ]; then
			garden-debian-sources-list "${sourcesListArgs[@]}" "$rootfs" "$suite"
		else
			# sbuild needs "deb-src" entries
			garden-debian-sources-list --deb-src "${sourcesListArgs[@]}" "$rootfs" "$suite"

			# schroot is picky about "/dev" (which is excluded by default in "garden-tar")
			# see https://github.com/debuerreotype/debuerreotype/pull/8#issuecomment-305855521
		fi

		case "$suite" in
			sarge)
				# for some reason, sarge creates "/var/cache/man/index.db" with some obvious embedded unix timestamps (but if we exclude it, "man" still works properly, so *shrug*)
				tarArgs+=( --exclude ./var/cache/man/index.db )
				;;

			woody)
				# woody not only contains "exim", but launches it during our build process and tries to email "root@debuerreotype" (which fails and creates non-reproducibility)
				tarArgs+=( --exclude ./var/spool/exim --exclude ./var/log/exim )
				;;

			potato)
				tarArgs+=(
					# for some reason, pototo leaves a core dump (TODO figure out why??)
					--exclude "./core"
					--exclude "./qemu*.core"
					# also, it leaves some junk in /tmp (/tmp/fdmount.conf.tmp.XXX)
					--exclude "./tmp/fdmount.conf.tmp.*"
				)
				;;
		esac

		garden-tar "${tarArgs[@]}" "$rootfs" "$targetBase.tar.xz"
		du -hsx "$targetBase.tar.xz"

		sha256sum "$targetBase.tar.xz" | cut -d" " -f1 > "$targetBase.tar.xz.sha256"
		touch_epoch "$targetBase.tar.xz.sha256"

		garden-chroot "$rootfs" bash -c '
			if ! dpkg-query -f='\''${binary:Package} ${Version}\n'\'' -W 2> /dev/null; then
				dpkg -l
			fi
		' > "$targetBase.manifest"
		echo "$epoch" > "$targetBase.garden-epoch"
		touch_epoch "$targetBase.manifest" "$targetBase.garden-epoch"

		for f in debian_version os-release apt/sources.list; do
			targetFile="$targetBase.$(basename "$f" | sed -r "s/[^a-zA-Z0-9_-]+/-/g")"
			if [ -e "$rootfs/etc/$f" ]; then
				cp "$rootfs/etc/$f" "$targetFile"
				touch_epoch "$targetFile"
			fi
		done

		echo "#### features"
		[ "$features" = "full" ] && features=$(ls $featureDir | paste -sd, -)
		for i in $(echo "base,$features" | tr ',' '\n' | norm_features); do
			if [ -s $featureDir/$i/image ]; then
				"$featureDir/$i/image" "$rootfs" "$targetBase"
			elif [ -f "$featureDir/$i/fstab" ]; then
				makeimage "$rootfs" "$targetBase.raw" < "$featureDir/$i/fstab"
			else
				true
			fi
		done
		echo "#### tests"
		[ "$features" = "full" ] && features=$(ls $featureDir | paste -sd, -)
		disabledBy=""
		enabledBy=""
		testcounter=0
		failcounter=0
		skipcounter=0

		# build the list of tests first
		echo "preparing apt lists in case we need to install packages for the tests"
		mkdir -p rootfs/etc/ssl
		mount --bind /etc/ssl rootfs/etc/ssl
		garden-apt-get rootfs update
		for t in $(find $featureDir/*/test/ -maxdepth 1 -type f -executable -exec basename {} \; | grep -v .disable | sort | uniq); do
			let "testcounter=testcounter+1"
			test=$(basename $t | cut -d. -f 1)
			if [ "${notests:-}" = 1 ]; then
				echo "test ${test} is being skipped, --skip-tests has been used"
				let "skipcounter=skipcounter+1"
				continue
			fi
			# go over features and build the enabled/disabled lists
			# a test with .disabled in a specific feature disables the test globally
			# a test that is not executable is not enabled for the specific feature
			for f in $(echo "base,$features" | tr ',' '\n' | norm_features); do
				featureTest="${featureDir}/${f}/test/${test}"
				if [ -f "${featureTest}.disable" ]; then
					disabledBy=$(echo "${f} ${disabledBy}")
					continue
				fi
				if [ -f "${featureTest}.chroot" ]; then
					if [ ! -x "${featureTest}.chroot" ]; then
						continue
					fi
					enabledBy=$(echo "${f} ${enabledBy}")
					continue
				fi
				if [ -f "${featureTest}" ]; then
					if [ ! -x "${featureTest}" ]; then
						continue
					fi
					enabledBy=$(echo "${f} ${enabledBy}")
				fi
			done
			if [ "$disabledBy" != "" ]; then
				echo "test ${test} is disabled by the following features: ${disabledBy}"
				# remove disabled tests that might be enabled in another feature
				enabledBy=$(echo $enabledBy |  tr " " "\n" | grep -vf <(echo $disabledBy | tr " " "\n"))
			elif [ "$enabledBy" != "" ]; then
				echo "test ${test} is enabled by the following features: ${enabledBy}"
				# prepare all other dependencies from the test
				for fd in $(echo "${enabledBy}"); do
					if [ -d "${featureDir}/${fd}/test/${test}.d" ]; then
						mkdir -p "${rootfs}/tmp/${test}.d"
						for fdep in "${featureDir}/${fd}/test/${test}.d"/*; do
							[ -e "$fdep" ] || continue
							fdepshort=$(basename $fdep)
							if [[ "$fdepshort" == "pkg.include" || "$fdepshort" == "pkg.exclude" ]]; then
								cat $fdep | filter_variables | filter_if >> "${rootfs}/tmp/${test}.d/${fdepshort}.list"
							else
								cat $fdep >> "${rootfs}/tmp/${test}.d/${fdepshort}"
							fi
						done
					fi
				done

				# move the actual tests from one of the features that enables it
				actualTest="${featureDir}/$(echo ${enabledBy} | awk '{ print $1 }')/test/${t}"
				cp -L ${actualTest} "${rootfs}/tmp/${test}"
				if [ ${t##*.} == "chroot" ]; then
					if garden-chroot "${rootfs}" ./tmp/${test}; then
						echo -e "\e[32mpassed\e[39m"
						echo
					else
						echo -e "\e[31mfailed\e[39m"
						echo
						let "failcounter=failcounter+1"
					fi
				else
					if "${rootfs}/tmp/${test}" ${rootfs} ${targetBase}; then
						echo -e "\e[32mpassed\e[39m"
						echo
					else
						echo -e "\e[31mfailed\e[39m"
						echo
						let "failcounter=failcounter+1"
					fi
				fi
				rm -rf "${rootfs}/tmp/${test}.d"
				rm -f "${rootfs}/tmp/$test"
			elif [ "$enabledBy" == "" ]; then
				echo "test ${test} is not enabled in any feature, skipping"
				let "skipcounter=skipcounter+1"
				echo
			fi
			disabledBy=""
			enabledBy=""
		done
		umount rootfs/etc/ssl
		echo "Tests done. ${failcounter}/${testcounter} failed. ${skipcounter}/${testcounter} skipped."
	}

	for rootfs in rootfs*/; do
		rootfs="${rootfs%/}" # "rootfs", "rootfs-slim", ...

		du -hsx "$rootfs"

		variant="${rootfs#rootfs}" # "", "-slim", ...
		variant="${variant#-}" # "", "slim", ...

		variantDir="$outputDir/$variant"
		mkdir -p "$variantDir"

		targetBase="${variantDir}rootfs"

		create_artifacts "$targetBase" "$rootfs" "$suite" "$variant"
	done

} >&2

if [ "${OUTPUT_DIR+defined}" ]; then
	echo
	echo ${outputDir}
else
	find "${outputDir}" -type f -exec install -v -m 0644 -p -o "${userID}" -g "${userGID}" {} "${volumeDir}" \;
fi
echo
if [ "$failcounter" -eq 0 ]; then
	echo "Done"
else
	echo "Done, but with errors"
	exit 1
fi
