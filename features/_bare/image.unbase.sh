#!/usr/bin/env bash

set -eufo pipefail

input_basename="$(basename "$1" | sed 's/\.tar.*$//g')"
output="$(realpath -- "$2")"

arch="$(echo "${input_basename}" | sed -E 's/^.*\-(\w*)\-\w*\-\w*$/\1/')"
cname="$(echo "${input_basename}" | sed 's/\-\w*\-\w*\-\w*$//g')"
flavor="$(echo "${input_basename}" | sed -E 's/(.*\-|^)(\w*)_bare\-.*$/\2/')"
version_data="$(echo "${input_basename}" | sed -E 's/^.*\-(\w*\-\w*)$/\1/')"

unbase_flavor="${flavor//_bare/}"
unbase_config_dir="/builder/features/${unbase_flavor}/unbase"

if [[ ! -f "${unbase_config_dir}/base" ]]; then
  echo "Failed locating the OCI image unbase base flavor: ${unbase_flavor}"
  exit 1
fi

base_cname="$(cat "${unbase_config_dir}/base")-$arch"
base_oci="$(dirname "$1")/${base_cname}-${version_data}.oci"

echo "Generating ${base_oci}"
make -C /builder "${base_oci}"

echo "Generating unbase_oci script for ${output}"

args=(--print-tree)

if [ -f "${unbase_config_dir}/mode" ]; then
	args+=("--$(cat "${unbase_config_dir}/mode")")
else
	args+=("--ldd-dependencies")
fi

if [ -f "${unbase_config_dir}/include" ]; then
	args+=(--include "\${base_path}/features/${unbase_flavor}/unbase/include")
fi

if [ -f "${unbase_config_dir}/exclude" ]; then
	args+=(--exclude "\${base_path}/features/${unbase_flavor}/unbase/exclude")
fi

if [ -f "${unbase_config_dir}/dpkg_include" ]; then
	args+=(--dpkg-include "\${base_path}/features/${unbase_flavor}/unbase/dpkg_include")
fi

cat > "$output" << EOF
#!/usr/bin/env bash

base_path=\$(realpath -- "\$(dirname -- "\${BASH_SOURCE[0]}")/..")

if [[ ! -f "\${base_path}/.build/${input_basename}.oci" ]]; then
  echo "Failed locating OCI image: ${cname}"
  exit 1
fi

if [[ ! -f "\${base_path}/.build/${input_basename}.oci.log" && -f "\${base_path}/.build/${input_basename}.orig.oci" ]]; then
  echo "Previous bare OCI build found: ${input_basename}.oci"
  exit 0
fi

echo "Generating bare OCI image: ${input_basename}.oci"
mv "\${base_path}/.build/${input_basename}.oci.log" "\${base_path}/.build/${input_basename}.orig.oci.log"
mv "\${base_path}/.build/${input_basename}.oci" "\${base_path}/.build/${input_basename}.orig.oci"
\${base_path}/unbase_oci ${args[@]} "\${base_path}/.build/${base_cname}-${version_data}.oci" "\${base_path}/.build/${input_basename}.orig.oci" "\${base_path}/.build/${input_basename}.oci"

if [ ! "\$(grep .orig.oci.log "\${base_path}/.build/${input_basename}.artifacts")" ]; then
  sed -i 's/${input_basename}\.oci\$/${input_basename}.orig.oci/' "\${base_path}/.build/${input_basename}.artifacts"
  sed -i 's/${input_basename}\.oci\.log\$/${input_basename}.orig.oci.log/' "\${base_path}/.build/${input_basename}.artifacts"
  echo '${input_basename}.oci' >> "\${base_path}/.build/${input_basename}.artifacts"
fi
EOF
