#!/usr/bin/env bash
set -e
# set -x

own_dir=ci # "$(readlink -f "$(dirname "${0}")")"

repo_root="${own_dir}/.."
bin_dir="${repo_root}/bin"

promote_target='snapshot'      # snapshot, release --> glci.model.PipelineFlavour
publishing_actions='manifests' # manifests, image, release --> glci.model.BuildType
gardenlinux_dir=$repo_root
branch_name="ci-dev"
# branch_name="main"
flavour_set='jens' # 'all'     # -> $gardenlinux_dir/flavours.yaml
# flavour_set='all'

git_url='https://github.com/gardenlinux/gardenlinux.git'
# git_url='https://github.com/jensh007/gardenlinux.git'
# git_url=`git config --get remote.origin.url`
oci_path='eu.gcr.io/gardener-project/test/gardenlinux-test'
tekton_namespace='jens'
disable_notification='true'

export PATH="${PATH}:${bin_dir}"


cleanup_pipelineruns() {
  echo "purging old pipelineruns"
  tkn \
    --namespace "${tekton_namespace}" \
    pipelineruns \
    delete \
    --force \
    --all \
    --keep 20
}

function get_latest_commit {
  git remote add cicdrepo ${git_url}
  git fetch cicdrepo ${branch_name}
  head_commit=`git rev-parse cicdrepo/${branch_name}`
  git remote rm cicdrepo
}

echo "render pipelines"
echo "gardenlinux_dir: ${gardenlinux_dir}"

get_latest_commit #"$(git rev-parse @)"
echo "Head commit: ${head_commit}"


pipeline_cfg="${gardenlinux_dir}/flavours.yaml"
outfile='rendered_pipeline.yaml'

# injected from pipeline_definitions
promote_target="${promote_target:-snapshot}"
publishing_actions="${publishing_actions:-manifests}"

if [ ! -z "${VERSION:-}" ]; then
  EXTRA_ARGS="--version=${VERSION}"
fi

echo "Skip cleanup step"
# cleanup_pipelineruns

pipeline_run="$PWD/pipeline_run.yaml"
rendered_task="$PWD/rendered_task.yaml"

# create pipeline-run for current commit
ci/render_pipeline_run.py $EXTRA_ARGS \
  --branch "${branch_name}" \
  --committish "${head_commit}" \
  --cicd-cfg 'default' \
  --flavour-set "${flavour_set}" \
  --promote-target "${promote_target}" \
  --publishing-action "${publishing_actions}" \
  --git-url "${git_url}" \
  --oci-path "${oci_path}" \
  --outfile "${pipeline_run}" \
  --disable-notification $disable_notification

ci/render_pipelines.py \
  --pipeline_cfg "${pipeline_cfg}" \
  --flavour-set "${flavour_set}" \
  --outfile "${outfile}"

ci/render_task.py \
  --outfile "${rendered_task}" \
  --use-secrets-server

# XXX hardcode other resources for now

for manifest in \
  "${rendered_task}" \
  "${outfile}" \
  "${pipeline_run}"
do
  #kubectl apply -n "${tekton_namespace}" -f "${manifest}"
  echo "Skip applying generated yamls"
done

echo 'done: rendering yamls for current commit'
