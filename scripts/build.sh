#!/usr/bin/env bash
set -Eeuo pipefail
set -x

epoch="$(date --date "$timestamp" +%s)"
serial="$(date --date "@$epoch" +%Y%m%d)"
dpkgArch="${arch:-$(dpkg --print-architecture | awk -F- "{ print \$NF }")}"

exportDir="output"
outputDir="$exportDir/$serial/$dpkgArch/$suite"

touch_epoch() {
	while [ "$#" -gt 0 ]; do
		local f="$1"; shift
		touch --no-dereference --date="@$epoch" "$f"
	done
}

debuerreotypeScriptsDir="$(dirname "$(readlink -f "$(which debuerreotype-init)")")"

for archive in "" security; do
	snapshotUrlFile="$exportDir/$serial/$dpkgArch/snapshot-url${archive:+-${archive}}"
	if [ -n "$ports" ] && [ -z "$archive" ]; then
		archive="ports"
	fi
	if [ -z "$eol" ]; then
		snapshotUrl="$("$debuerreotypeScriptsDir/.snapshot-url.sh" "@$epoch" "${archive:+debian-${archive}}")"
	else
		snapshotUrl="$("$debuerreotypeScriptsDir/.snapshot-url.sh" "@$epoch" "debian-archive")/debian${archive:+-${archive}}"
	fi
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

	if [ -n "$ports" ]; then
		gpg --batch --no-default-keyring --keyring "$keyring" --import \
			/usr/share/keyrings/debian-ports-archive-keyring.gpg
	fi
fi

snapshotUrl="$(< "$exportDir/$serial/$dpkgArch/snapshot-url")"
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

codename="$(awk -F ": " "\$1 == \"Codename\" { print \$2; exit }" "$outputDir/Release")"

{
	initArgs=( --arch="$dpkgArch" )
	if [ -z "$eol" ]; then
		initArgs+=( --debian )
	else
		initArgs+=( --debian-eol )
	fi
	if [ -n "$ports" ]; then
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

	if [ -n "$qemu" ]; then
		initArgs+=( --debootstrap="qemu-debootstrap" )
	fi

	debuerreotype-init "${initArgs[@]}" rootfs "$suite" "@$epoch"

	if [ -n "$eol" ]; then
		debuerreotype-gpgv-ignore-expiration-config rootfs
	fi

	[ -n "$features" ] && configArgs+=( --features "$features" )

	debuerreotype-minimizing-config "${configArgs[@]}" rootfs
	debuerreotype-apt-get rootfs update -qq
	debuerreotype-apt-get rootfs dist-upgrade -yqq

	aptVersion="$("$debuerreotypeScriptsDir/.apt-version.sh" rootfs)"
	if [ -n "$eol" ] && dpkg --compare-versions "$aptVersion" ">=" "0.7.26~"; then
		# https://salsa.debian.org/apt-team/apt/commit/1ddb859611d2e0f3d9ea12085001810f689e8c99
		echo "Acquire::Check-Valid-Until \"false\";" > rootfs/etc/apt/apt.conf.d/check-valid-until.conf
		# TODO make this a real script so it can have a nice comment explaining why we do it for EOL releases?
	fi

	# make a couple copies of rootfs so we can create other variants
	#for variant in slim sbuild; do
	#	mkdir "rootfs-$variant"
	#	tar -cC rootfs . | tar -xC "rootfs-$variant"
	#done

	debuerreotype-slimify rootfs

	sourcesListArgs=()
	[ -z "$eol" ] || sourcesListArgs+=( --eol )
	[ -z "$ports" ] || sourcesListArgs+=( --ports )

	create_artifacts() {
		local targetBase="$1"; shift
		local rootfs="$1"; shift
		local suite="$1"; shift
		local variant="$1"; shift

		# make a copy of the snapshot-facing sources.list file before we overwrite it
		cp "$rootfs/etc/apt/sources.list" "$targetBase.sources-list-snapshot"
		touch_epoch "$targetBase.sources-list-snapshot"

		local tarArgs=()
		if [ -n "$qemu" ]; then
			tarArgs+=( --exclude="./usr/bin/qemu-*-static" )
		fi
			
		tarArgs+=( --include-dev )

		if [ "$variant" != "sbuild" ]; then
			debuerreotype-debian-sources-list "${sourcesListArgs[@]}" "$rootfs" "$suite"
		else
			# sbuild needs "deb-src" entries
			debuerreotype-debian-sources-list --deb-src "${sourcesListArgs[@]}" "$rootfs" "$suite"

			# schroot is picky about "/dev" (which is excluded by default in "debuerreotype-tar")
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

		debuerreotype-tar "${tarArgs[@]}" "$rootfs" "$targetBase.tar.xz"
		du -hsx "$targetBase.tar.xz"

		sha256sum "$targetBase.tar.xz" | cut -d" " -f1 > "$targetBase.tar.xz.sha256"
		touch_epoch "$targetBase.tar.xz.sha256"

		debuerreotype-chroot "$rootfs" bash -c '
			if ! dpkg-query -f='\''\${binary:Package} \${Version}\n'\'' -W 2> /dev/null; then
				# --debian-eol woody has no dpkg-query
				dpkg -l
			fi
		' > "$targetBase.manifest"
		echo "$epoch" > "$targetBase.debuerreotype-epoch"
		debuerreotype-version > "$targetBase.debuerreotype-version"
		touch_epoch "$targetBase.manifest" "$targetBase.debuerreotype-epoch" "$targetBase.debuerreotype-version"

		for f in debian_version os-release apt/sources.list; do
			targetFile="$targetBase.$(basename "$f" | sed -r "s/[^a-zA-Z0-9_-]+/-/g")"
			if [ -e "$rootfs/etc/$f" ]; then
				# /etc/os-release does not exist in --debian-eol squeeze, for example (hence the existence check)
				cp "$rootfs/etc/$f" "$targetFile"
				touch_epoch "$targetFile"
			fi
		done

		featureDir=/opt/debuerreotype/features
		[ "$features" = "full" ] && features=$(ls $featureDir | paste -sd, -)
		for i in $(echo "base,$features" | tr ',' ' ' | sort -u); do
			[ -s $featureDir/$i/image ] && bash -c "$featureDir/$i/image /tmp/$targetBase $targetBase.tar.xz"
		done

		echo "Errorlevel: $?"
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

	if [ "$codename" != "$suite" ]; then
		codenameDir="$exportDir/$serial/$dpkgArch/$codename"
		mkdir -p "$codenameDir"
		tar -cC "$outputDir" --exclude="**/rootfs.*" . | tar -xC "$codenameDir"

		for rootfs in rootfs*/; do
			rootfs="${rootfs%/}" # "rootfs", "rootfs-slim", ...

			variant="${rootfs#rootfs}" # "", "-slim", ...
			variant="${variant#-}" # "", "slim", ...

			variantDir="$codenameDir/$variant"
			targetBase="$variantDir/rootfs"

			# point sources.list back at snapshot.debian.org temporarily (but this time pointing at $codename instead of $suite)
			debuerreotype-debian-sources-list --snapshot "${sourcesListArgs[@]}" "$rootfs" "$codename"

			create_artifacts "$targetBase" "$rootfs" "$codename" "$variant"
		done
	fi
} >&2

tar --sparse -cC "$exportDir" .
