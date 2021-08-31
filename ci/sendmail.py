#!/usr/bin/env python3
from email.mime.base import MIMEBase
import email
import ci.util
import glci.notify
import glci.util
import os
from string import Template


body = '''
<!DOCTYPE html><html>
<head>
<meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8">
</head>
<body>
<p> First paragraph </p>
<div id='abc'>
<p> Second paragraph </p>
</div>
<hr>
<footer>
<p><small>This email is sent to <a href=3D"https://github.com/garde=
nlinux/gardenlinux/blob/main/CODEOWNERS">CODEOWNERS </a>of the GardenLinux r=
epository.</small>
</p>
</footer>
</body>
</html>
'''


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


def main():
    cicd_cfg = glci.util.cicd_cfg(cfg_name='default')
    email_cfg = _email_cfg(cicd_cfg=cicd_cfg)

    repo_dir = '/Users/d058463/git/gardenlinux'
    template_path = os.path.abspath(os.path.join(repo_dir,"ci/templates/email_notification.html"))
    with open(template_path, 'r') as mail_template_file:
        mail_template = mail_template_file.read()

    # read the logo
    logo_path = os.path.abspath(os.path.join(repo_dir,"logo/gardenlinux.svg"))
    with open(logo_path, 'r') as logo_file:
        logo_svg = logo_file.read()

    # replace id and add some attributes
    # logo_svg = logo_svg.replace('<svg id="Layer_1"', '<svg id="gl_logo" width="100px"')
    # logo_svg = logo_svg.replace('<title>Garden Linux_logo</title>',
    #     '<title>Garden Linux Logo</title>')

    result_table = '<tr><td class="align_left">foo</td><td>bar</td></tr>'

    # fill template parameters:
    html_template = Template(mail_template)
    values = {
        'pipeline': 'pipeline_name',
        'status_table': result_table,
        'pipeline_run': 'pipeline_run_name',
        'namespace': 'namespace',
        'logo_src': logo_svg,
    }

    pipeline_run_name = 'my_pipeline_run'
    namespace = 'jens'

    plain_text_body = f'''
    Garden Linux Build Pipeline: {pipeline_run_name}

    Notification from the Garden Linux Build Pipeline: Failure in pipeline {pipeline_run_name}.
    The pipeline run {pipeline_run_name} running in namespace {namespace} failed in at least one task.
    '''

    recipients = ['jens.huebel@gmx.de', 'j.huebel@sap.com']
    # filter recipients for crippled providers like gmx dropping too complex emails:
    recipients_crippled = [recp for recp in recipients if recp.endswith('gmx.de')]
    # recipients = [recp for recp in recipients if recp not in recipients_crippled]

    # generate mail body
    mail_body = html_template.safe_substitute(values)
    subject = 'Test-Mail from Python'

    print(f'Send html notification to following recipients: {recipients}')
    mail_msg = glci.notify.mk_html_mail_body(
        text=mail_body,
        recipients=recipients,
        subject=subject,
        sender=email_cfg.sender_name(),
    )
    _attach_and_send(repo_dir=repo_dir, mail_msg=mail_msg, email_cfg=email_cfg)

    # print(f'Send plain text notification to following recipients: {recipients_crippled}')
    # mail_msg = glci.notify.mk_plain_text_body(
    #     text=plain_text_body,
    #     recipients=recipients_crippled,
    #     subject=subject,
    #     sender=email_cfg.sender_name(),
    # )
    # _attach_and_send(repo_dir=repo_dir, mail_msg=mail_msg, email_cfg=email_cfg)

    mail_client = _smtp_client(email_cfg=email_cfg)
    mail_client.send_message(msg=mail_msg)


if __name__ == '__main__':
    main()
