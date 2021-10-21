import ccc.github
import ci.util
import distutils.util
from email.mime.base import MIMEBase
import email.message
import glci.notify
import glci.util
import json
import mailutil
import os
from string import Template
import urllib
import typing


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
            part = MIMEBase('application', "zip")
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
    additional_recipients: str = None,
    only_recipients: str = None,
    recipients_plaintext: typing.Sequence[str] = [],
):
    if distutils.util.strtobool(disable_notifications):
        print('Notification is disabled, not sending email')
        return

    additional_recipients_set = set(additional_recipients.strip().split(';'))
    only_recipients_set = set(only_recipients.strip().split(';'))
    # remove empty elements because split of an empty string gives a list with an empty elem
    additional_recipients_set = {elem for elem in additional_recipients_set if elem}
    only_recipients_set = {elem for elem in only_recipients_set if elem}
    print(f'sending to additional recipients: {additional_recipients_set}')
    print(f'sending only to recipients: {only_recipients_set}')

    status_dict = json.loads(status_dict_str)
    must_send = True in [True for status in status_dict.values() if status != 'Succeeded']

    if not must_send:
        print("All tasks succeded, no notification sent")
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

    subject = f'Tekton Pipeline Garden Linux build failure in {pipeline_name}'
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

    dashboard_url = f'https://tekton-dashboard.gardenlinux.io/#/namespaces/{namespace}/pipelineruns/{pipeline_run_name}'

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

    # fill template parameters:
    html_template = Template(html_mail_template)
    txt_template = Template(txt_mail_template)
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
    }

    # generate mail body
    html_mail_body = html_template.safe_substitute(values)
    values['status_table'] = txt_result_table
    txt_mail_body = txt_template.safe_substitute(values)

    # if only_recipients are set do not get defaults from codeowners
    if only_recipients_set:
        recipients = only_recipients_set
    else:
        print("getting recipients from CODEOWNERS")
        parsed_url = urllib.parse.urlparse(giturl)
        github_cfg = ccc.github.github_cfg_for_hostname(parsed_url.hostname)
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
        print('Mail not sent, could not find any recipient.')
        return

    # filter recipients for those who should get plain-text emails:
    # Note currently unused, but left as option for future configuration
    recipients = [recp for recp in recipients if recp not in recipients_plaintext]

    print(f'Send html notification to following recipients: {recipients}')
    if recipients:
        mail_msg = glci.notify.mk_html_mail_body(
            text=html_mail_body,
            recipients=recipients,
            subject=subject,
            sender=email_cfg.sender_name(),
        )
        _attach_and_send(repo_dir=repo_dir, mail_msg=mail_msg, email_cfg=email_cfg)

    print(f'Send plain text notification to following recipients: {recipients_plaintext}')
    if recipients_plaintext:
        mail_msg = _mk_plain_text_body(
            text=txt_mail_body,
            recipients=recipients_plaintext,
            subject=subject,
            sender=email_cfg.sender_name(),
        )
        _attach_and_send(repo_dir=repo_dir, mail_msg=mail_msg, email_cfg=email_cfg)
