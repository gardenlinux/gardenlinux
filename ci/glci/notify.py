import email
import email.message
import email.mime.multipart
import email.mime.text
import smtplib
import typing

import git
import html2text

import paths


def determine_email_notification_recipients(repo_root=paths.repo_root):
    repo = git.Repo(path=repo_root)
    head_commit = repo.head.commit

    recipients = set((head_commit.author.email, head_commit.committer.email))
    return recipients


def smtp_client(
    host: str,
    user: str,
    passwd: str,
) -> smtplib.SMTP:
    client = smtplib.SMTP_SSL(host=host)
    client.login(user=user, password=passwd)

    return client


def mk_html_mail_body(
    text: str,
    recipients: typing.Sequence[str],
    subject: str,
    sender: str,
) -> email.message.EmailMessage:
    msg = email.mime.multipart.MIMEMultipart(subtype='mixed')

    message_html = email.mime.text.MIMEText(
        text,
        'html',
    )
    message_plain = email.mime.text.MIMEText(
        html2text.html2text(text),
        'text'
    )

    msg.attach(message_html)
    msg.attach(message_plain)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    return msg


def mk_plain_text_body(
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


def send_mail(
    sender: str,
    message: email.message.EmailMessage,
    client: smtplib.SMTP,
):
    client.send_message(
        from_addr=sender,
        msg=message,
    )
