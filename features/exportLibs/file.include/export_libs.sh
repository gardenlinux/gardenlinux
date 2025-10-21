#!/usr/bin/env bash

function is_elf {
	[ "$(od -A n -t x1 -N 4 "$1" | tr -d ' ')" = "7f454c46" ]
}

function elf_arch {
	case "$(od -A n -t d1 -j 5 -N 1 "$1" | tr -d ' ')" in
		1)
			local endian=little
			;;
		2)
			local endian=big
			;;
		*)
			return 1
			;;
	esac
	case "$(od --endian "$endian" -A n -t x2 -j 18 -N 2 "$1" | tr -d ' ')" in
		0003)
			local arch=i686
			;;
		003e)
			local arch=x86_64
			;;
		00b7)
			local arch=aarch64
			;;
		*)
			return 1
			;;
	esac
	echo "$arch"
}

mkdir required_libs

packages=$(python3 -c 'import site; print(site.getsitepackages()[0])')

find "$packages" | while read -r file; do
		if [ ! -L "$file" ] && [ -f "$file" ]; then
			if is_elf "$file"; then
				interpreter=
				if ! interpreter="$(patchelf --print-interpreter "$file" 2> /dev/null)"; then
					case "$(elf_arch "$file")" in
						i686)
							interpreter=/lib/ld-linux.so.2
							;;
						x86_64)
							interpreter=/lib64/ld-linux-x86-64.so.2
							;;
						aarch64)
							interpreter=/lib/ld-linux-aarch64.so.1
							;;
					esac
				fi
				if [ -n "$interpreter" ]; then
					# segfaults for go binaries if running under qemu-user-static emulation => always return true
					{ "$interpreter" --inhibit-cache --list "$file" 2> /dev/null || true; } | sed 's/^.*=>//;s/^\s*//;s/\s*(\w*)$//' | { grep '^/' || [ $? = 1 ]; }
				fi
			fi
		fi
	done | while read -r file; do
		realpath "$file"
	done | sort -u | while read -r file; do
		mkdir -p "$(dirname "required_libs$file")" && cp "$file" "required_libs$file"
	done
