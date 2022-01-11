import distutils.util
import email.message
import email.mime.base
import json
import logging
import os
import string
import sys
import typing
import urllib

import ccc.github
import ccc.slack
import ci.util
import glci.github
import glci.notify
import glci.util
import mailutil


logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


def _email_cfg(cicd_cfg: glci.model.CicdCfg):
    ctx = ci.util.ctx()
    cfg_factory = ctx.cfg_factory()
    return cfg_factory.email(cfg_name=cicd_cfg.notify.email_cfg_name)


def _smtp_client(email_cfg):
    return glci.notify.smtp_client(
        host=email_cfg.smtp_host(),
        user=email_cfg.credentials().username(),
        passwd=email_cfg.credentials().passwd(),
)


def _attach_and_send(
    repo_dir: str,
    mail_msg: email.message.EmailMessage,
    email_cfg,
):
    # check if there is a log file to attach
    log_zip_name = 'build_log.zip'
    log_zip = os.path.join(repo_dir, log_zip_name)
    if os.path.exists(log_zip):
        with open(log_zip, 'rb') as att_file:
            zip_data = att_file.read()
        if mail_msg.is_multipart():
            part = email.mime.base.MIMEBase('application', "zip")
            part.set_payload(zip_data)
            email.encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{log_zip_name}"')
            mail_msg.attach(part)
        else:
            mail_msg.add_attachment(
                zip_data,
                maintype='application',
                subtype='zip',
                filename=log_zip_name,
            )
    # for debugging generate a local file
    # with open('email_out.html', 'w') as file:
    #     file.write(mail_body)

    mail_client = _smtp_client(email_cfg=email_cfg)
    mail_client.send_message(msg=mail_msg)


def _mk_plain_text_body(
    text: str,
    recipients: typing.Sequence[str],
    subject: str,
    sender: str,
) -> email.message.EmailMessage:
    msg = msg = email.message.EmailMessage()
    msg.set_content(text)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    return msg


def _post_to_slack(
    repo_dir: str,
    branch_name: str,
    dashboard_url: str,
    slack_cfg_name: str,
    channel: str,
    title: str,
):
    ctx = ci.util.ctx()
    cfg_factory = ctx.cfg_factory()

    slack_cfg = cfg_factory.slack(slack_cfg_name)
    slack_client = ccc.slack.client(slack_cfg)

    log_zip_name = 'build_log.zip'
    log_zip = os.path.join(repo_dir, log_zip_name)
    if os.path.exists(log_zip):
        logger.info('Posting notification to slack channel and attaching build log')
        response = slack_client.files_upload(
            file=log_zip,
            channels=channel,
            initial_comment=(
                f'Tekton Pipeline for branch `{branch_name}` failed. To see the job in the '
                f'dashboard, use the following link: {dashboard_url}'
            ),
            title=title,
            filetype='zip',
        )
    else:
        logger.info('Posting notification to slack channel')
        response = slack_client.chat_postMessage(
            channel=channel,
            text=(
                f'Tekton Pipeline for branch `{branch_name}` failed. To see the job in the '
                f'dashboard, use the following link: {dashboard_url}.\n '
                'No build log available'
            )
        )

    if not response['ok']:
        raise RuntimeError(f"failed to post to slack channel '{channel}': {response['error']}")


def send_notification(
    branch: str,
    cicd_cfg_name: str,
    committish: str,
    disable_notifications: str,
    namespace: str,
    giturl: str,
    pipeline_name: str,
    pipeline_run_name: str,
    repo_dir: str,
    status_dict_str: str,
    pr_id: str = None,
    additional_recipients: str = None,
    only_recipients: str = None,
    recipients_plaintext: typing.Sequence[str] = [],
):
    dashboard_url = (
        f'https://tekton-dashboard.gardenlinux.io/#/namespaces/{namespace}'
        f'/pipelineruns/{pipeline_run_name}'
    )

    status_dict = json.loads(status_dict_str)
    task_failed = not all([
        True if status == 'Succeeded' else False
        for status in status_dict.values()
    ])

    parsed_url = urllib.parse.urlparse(giturl)
    github_cfg = ccc.github.github_cfg_for_hostname(parsed_url.hostname)

    if task_failed:
        status_to_report = glci.github.GitHubStatus.FAILURE
    else:
        status_to_report = glci.github.GitHubStatus.SUCCESS

    glci.github.post_github_status(
        git_url=giturl,
        committish=committish,
        state=status_to_report,
        target_url=dashboard_url,
        description='Pipeline run finished',
    )

    if distutils.util.strtobool(disable_notifications):
        logger.info('Notification is disabled, not sending email')
        return
    if pr_id and int(pr_id) > 0:
        # don't send any sort of notification for PR-builds
        return

    additional_recipients_set = set(additional_recipients.strip().split(';'))
    only_recipients_set = set(only_recipients.strip().split(';'))
    # remove empty elements because split of an empty string gives a list with an empty elem
    additional_recipients_set = {elem for elem in additional_recipients_set if elem}
    only_recipients_set = {elem for elem in only_recipients_set if elem}
    logger.info(f'sending to additional recipients: {additional_recipients_set}')
    logger.info(f'sending only to recipients: {only_recipients_set}')

    must_send = True in [True for status in status_dict.values() if status != 'Succeeded']

    if not must_send:
        logger.info("All tasks succeded, no notification sent")
        return

    html_result_table = ""
    for task, status in status_dict.items():
        if status == 'Succeeded':
            status_symbol = '&#9989;'
        elif status == 'Failed':
            status_symbol = '&#10060;'
        else:
            status_symbol = '?'

        html_result_table += f'<tr><td class="align_left">{task}</td><td>{status_symbol}</td></tr>'

    txt_result_table = ""
    for task, status in status_dict.items():
        txt_result_table += f'Task: {task}\nStatus: {status}\n'

    subject = f'Garden Linux build failure in {pipeline_name} in branch {namespace}'
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    email_cfg = _email_cfg(cicd_cfg=cicd_cfg)

    html_template_path = os.path.abspath(
        os.path.join(repo_dir, "ci/templates/email_notification.html")
    )
    with open(html_template_path, 'r') as mail_template_file:
        html_mail_template = mail_template_file.read()

    txt_template_path = os.path.abspath(
        os.path.join(repo_dir, "ci/templates/email_notification.txt")
    )
    with open(txt_template_path, 'r') as mail_template_file:
        txt_mail_template = mail_template_file.read()

    # read the logo
    logo_path = os.path.abspath(os.path.join(repo_dir,"logo/gardenlinux_minified.svg"))
    with open(logo_path, 'r') as logo_file:
        logo_svg = logo_file.read()

    # replace id and add some attributes
    logo_svg = logo_svg.replace('<svg data-name="Layer 1"', '<svg data-name="gl_logo" width="100px"')

    # read the S3 download URL for the full log file:
    s3_path = os.path.join(repo_dir, 'log_url.txt')
    if os.path.exists(s3_path):
        with open(s3_path) as f:
            log_url = f.readline()
        log_url_href = log_url.strip()
        log_url_descr = 'here'
    else:
        log_url_href = "#"
        log_url_descr = '<not available>'

    # get log excerpts:
    log_path = os.path.join(repo_dir, 'failed_summary.txt')
    if os.path.exists(log_path):
        with open(log_path) as f:
            log_text = f.read()
    else:
        log_text = '<Logs not available.>'

    # fill template parameters:
    html_template = string.Template(html_mail_template)
    txt_template = string.Template(txt_mail_template)
    values = {
        'branch': branch,
        'commit': committish,
        'pipeline': pipeline_name,
        'status_table': html_result_table,
        'dashboard_url': dashboard_url,
        'namespace': namespace,
        'logo_src': logo_svg,
        'log_url_href': log_url_href,
        'log_url_descr': log_url_descr,
        'pipeline_run': pipeline_run_name,
        'log_excerpt': log_text,
    }

    # generate mail body
    html_mail_body = html_template.safe_substitute(values)

    values['status_table'] = txt_result_table
    txt_mail_body = txt_template.safe_substitute(values)

    # if only_recipients are set do not get defaults from codeowners
    if only_recipients_set:
        recipients = only_recipients_set
    else:
        logger.info("getting recipients from CODEOWNERS")
        github_api = ccc.github.github_api(github_cfg)
        codeowners = mailutil.determine_local_repository_codeowners_recipients(
            github_api=github_api,
            src_dirs=(repo_dir,),
        )
        # eliminate duplicates by converting it to a set:
        recipients = {r for r in codeowners}

    # add given additional recipients
    recipients |= additional_recipients_set
    if len(recipients) == 0:
        logger.warning('Mail not sent, could not find any recipient.')
        return

    # filter recipients for those who should get plain-text emails:
    # Note currently unused, but left as option for future configuration
    recipients = [recp for recp in recipients if recp not in recipients_plaintext]

    logger.info(f'Send html notification to following recipients: {recipients}')
    if recipients:
        mail_msg = glci.notify.mk_html_mail_body(
            text=html_mail_body,
            recipients=recipients,
            subject=subject,
            sender=email_cfg.sender_name(),
        )
        _attach_and_send(repo_dir=repo_dir, mail_msg=mail_msg, email_cfg=email_cfg)

    logger.info(f'Send plain text notification to following recipients: {recipients_plaintext}')
    if recipients_plaintext:
        mail_msg = _mk_plain_text_body(
            text=txt_mail_body,
            recipients=recipients_plaintext,
            subject=subject,
            sender=email_cfg.sender_name(),
        )
        _attach_and_send(repo_dir=repo_dir, mail_msg=mail_msg, email_cfg=email_cfg)

    if branch in cicd_cfg.notify.branches:
        # prevent slack-messages from manually generated/deployed test-pipelines. These are
        # sometimes created _from_ the main branch, but deployed to a manually selected tekton-
        # namespace
        if namespace == branch:
            _post_to_slack(
                repo_dir=repo_dir,
                branch_name=branch,
                dashboard_url=dashboard_url,
                slack_cfg_name=cicd_cfg.notify.slack_cfg_name,
                channel=cicd_cfg.notify.slack_channel,
                title='Build Logs',
            )

    # check if we have a status file indicating that some previous step failed, exit with error then
    status_txt = os.path.join(repo_dir, 'status.txt')
    if os.path.exists(status_txt):
        with open() as f:
            err = f.read()
            print(f'Exiting with error, one of the previous steps failed with: {err}')
            sys.exit(1)
