#! /usr/bin/env python3
import sys
sys.path.insert(1, '/Users/d058463/git/gardenlinux/ci/steps')
import attach_logs  # noqa:E402


if __name__ == '__main__':
    attach_logs.upload_logs(
        architecture='amd64',
        cicd_cfg_name='default',
        committish='02b546edddb698b911d753c5b9bdd3f4e0549818',
        gardenlinux_epoch='518',
        modifiers='_nopkg,_prod,_readonly,_slim,base,cloud,gardener,server',
        namespace='jens',
        pipeline_run_name='gardenlinux-man-tst-518-0-57101f-3206',
        platform='aws',
        repo_dir='/Users/d058463/git/gardenlinux',
        version='518.0',
    )
