#!/usr/bin/env python3

import argparse
import logging

import git
import yaml

import ci.util

import glci.notify
import glci.util
import glci.model
import tkn.util
import paths

logger = logging.getLogger(__name__)


def _email_cfg(cicd_cfg: glci.model.CicdCfg):
    ctx = ci.util.ctx()
    cfg_factory = ctx.cfg_factory()
    return cfg_factory.email(cfg_name=cicd_cfg.notify.email_cfg_name)


def _smtp_client(cicd_cfg: glci.model.CicdCfg):
    email_cfg = _email_cfg(cicd_cfg=cicd_cfg)

    return glci.notify.smtp_client(
        host=email_cfg.smtp_host(),
        user=email_cfg.credentials().username(),
        passwd=email_cfg.credentials().passwd(),
    )


def notify(
    pipelinerun_name: str,
    namespace: str,
    cicd_cfg: glci.model.CicdCfg,
):
    email_cfg = _email_cfg(cicd_cfg=cicd_cfg)
    task_status = tkn.util.pipeline_taskrun_status(name=pipelinerun_name, namespace=namespace)

    for failed_info in task_status.failed_details:
        logger.warning(f'{failed_info["name"]=} failed with {failed_info["message"]}')

    failed_task_names = [fd['name'] for fd in task_status.failed_details]
    failed_tname_html = '\n'.join([f'<li>{name}</li>' for name in failed_task_names])

    recipients = glci.notify.determine_email_notification_recipients()

    repo = git.Repo(paths.repo_root)
    head_commit = repo.head.commit
    committish = head_commit.hexsha
    commit_msg = head_commit.message

    mail_html = f'''
        <em>This is to inform you about a build error</em>
        <ul>
            <li>committish: {committish}</li>
            <li>commit-msg: {commit_msg}</li>
        </ul>
        The following pipeline tasks failed:
        <ul>
            {failed_tname_html}
        </ul>
    '''

    mail_msg = glci.notify.mk_html_mail_body(
        text=mail_html,
        recipients=recipients,
        subject='[Action Required] - gardenlinux build failed',
        sender=email_cfg.sender_name(),
    )

    glci.notify.send_mail(
        sender=email_cfg.sender_name(),
        recipients=recipients,
        message=mail_msg,
        client=_smtp_client(cicd_cfg=cicd_cfg),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pipelinerun-name')
    parser.add_argument('--pipelinerun-file')
    parser.add_argument('--namespace')
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--send-notification', action=argparse.BooleanOptionalAction, default=False)

    parsed = parser.parse_args()

    pipelinerun_name = parsed.pipelinerun_name
    pipelinerun_file = parsed.pipelinerun_file
    namespace = parsed.namespace
    cicd_cfg = glci.util.cicd_cfg(cfg_name=parsed.cicd_cfg)

    if not bool(pipelinerun_file) ^ bool(pipelinerun_name):
        raise ValueError('exactly ony of pipelinerun-name or -file must be given')

    if pipelinerun_file:
        with open(pipelinerun_file) as f:
            parsed_pipelinerun = yaml.safe_load(f)
            metadata = parsed_pipelinerun['metadata']
            pipelinerun_name = metadata['name']

    logger.info(f'waiting for {pipelinerun_name=} to finish')

    try:
        tkn.util.wait_for_pipelinerun_status(
            name=pipelinerun_name,
            namespace=namespace,
        )
        logger.info('{pipelinerun=} succeeded')

    except RuntimeError as rte:
        logger.error(rte)
        logger.error('pipeline run failed')
        if parsed.send_notification:
            notify(
                pipelinerun_name=pipelinerun_name,
                namespace=namespace,
                cicd_cfg=cicd_cfg,
            )
        raise rte


if __name__ == '__main__':
    main()
