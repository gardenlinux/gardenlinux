own_dir="$(readlink -f "$(dirname "${0}")")"
repo_root="$(readlink -f "${own_dir}/..")"
bin_dir="${repo_root}/bin"

function install_kubectl() {
  if which kubectl &>/dev/null; then
    return 0
  fi

  # XXX install kubectl (should rather be installed into container-image)
  curl -Lo /bin/kubectl \
    https://storage.googleapis.com/kubernetes-release/release/v1.18.2/bin/linux/amd64/kubectl
  chmod +x /bin/kubectl
}

function install_tkn() {
  if which tkn &>/dev/null; then
    return 0
  fi
  curl -L \
    https://github.com/tektoncd/cli/releases/download/v0.10.0/tkn_0.10.0_Linux_x86_64.tar.gz \
    | tar xz -C /bin
}

function kubecfg()  {
  shootcluster_cfg_name="$(gardener-ci \
    config attribute \
     --cfg-type cfg_set \
     --cfg-name gardenlinux \
     --key kubernetes.default \
  )"

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
  export BRANCH_NAME="${BRANCH_NAME:-main}"
  export FLAVOUR_SET="${FLAVOUR_SET:-all}"
  export GARDENLINUX_TKN_WS="${GARDENLINUX_TKN_WS:-gardenlinux}"
  export GIT_URL="${GIT_URL:-https://github.com/gardenlinux/gardenlinux}"
  export OCI_PATH="${OCI_PATH:-eu.gcr.io/gardener-project/gardenlinux}"
  export PROMOTE_TARGET="${PROMOTE_TARGET:-snapshot}"
  export BUILD_TARGETS="${BUILD_TARGETS:-build}"
  export PATH="${PATH}:${bin_dir}"
}
