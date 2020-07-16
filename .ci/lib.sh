own_dir="$(readlink -f "$(dirname "${0}")")"
repo_root="$(readlink -f "${own_dir}/..")"
bin_dir="${repo_root}/bin"

cfgset_name="${CONCOURSE_CURRENT_CFG}"
shootcluster_cfg_name="$(gardener-ci \
  config attribute \
   --cfg-type cfg_set \
   --cfg-name "${cfgset_name}" \
   --key kubernetes.default \
)"

function install_kubectl() {
  if which kubectl &>/dev/null; then
    exit 0
  fi

  # XXX install kubectl (should rather be installed into container-image)
  curl -Lo /bin/kubectl \
    https://storage.googleapis.com/kubernetes-release/release/v1.18.2/bin/linux/amd64/kubectl
  chmod +x /bin/kubectl
}

function install_tkn() {
  if which tkn &>/dev/null; then
    exit 0
  fi
  curl -L \
    https://github.com/tektoncd/cli/releases/download/v0.10.0/tkn_0.10.0_Linux_x86_64.tar.gz \
    | tar xz -C /bin
}

function kubecfg()  {
  # retrieve kubeconfig
  gardener-ci config model_element \
    --cfg-type kubernetes \
    --cfg-name "${shootcluster_cfg_name}" \
    --key kubeconfig \
  > kubeconfig
  export KUBECONFIG="$PWD/kubeconfig"
  ls -la "${KUBECONFIG}"
}

function export_env() {
  export GARDENLINUX_TKN_WS='gardenlinux-tkn'
  export BRANCH_NAME="${GARDENLINUX_BRANCH}"
  # XXX hardcode for now
  export FLAVOUR_SET='all'
  export PATH="${PATH}:${bin_dir}"
}
