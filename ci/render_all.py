#!/usr/bin/env python3
import argparse
import paths
import render_pipelines
import render_task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--pipeline_cfg',
        default=paths.flavour_cfg_path,
    )
    parser.add_argument(
        '--flavour-set',
        default='all',
    )
    parser.add_argument(
        '--outfile-pipeline-main',
        default='pipeline.yaml',
    )
    parser.add_argument(
        '--outfile-pipeline-packages',
        default='pipeline-packages.yaml',
    )
    # for tasks:
    parser.add_argument('--use-secrets-server', action='store_true')
    parser.add_argument('--outfile-tasks', default='tasks.yaml')
    parser.add_argument('--skip-cfssl-build', action='store_true')

    parsed = parser.parse_args()

    # Render tasks:
    all_tasks = render_task.render_task(
        skip_cfssl_build=parsed.skip_cfssl_build,
        use_secrets_server=parsed.use_secrets_server,
        outfile_tasks=parsed.outfile_tasks,
    )

    # Render pipelines:
    render_pipelines.render_pipelines(
        build_yaml=parsed.pipeline_cfg,
        flavour_set=parsed.flavour_set,
        outfile_pipeline_main=parsed.outfile_pipeline_main,
        outfile_pipeline_packages=parsed.outfile_pipeline_packages,
        tasks=all_tasks,
    )


if __name__ == '__main__':
    main()
