import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

email = os.environ.get('GOOGLE_EMAIL')


def smtp_setting():
    mail_type = 'smtp.gmail.com'
    port = os.environ.get('GOOGLE_EMAIL_PORT')

    password = os.environ.get('GOOGLE_EMAIL_PASSWORD')

    smtp = smtplib.SMTP(mail_type, port)
    smtp.set_debuglevel(True)

    smtp.ehlo()
    smtp.starttls()
    smtp.login(email, password)

    return smtp


def send_plain_mail(receiver,subject, content):
    smtp = smtp_setting()

    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = os.environ.get('GOOGLE_EMAIL')
    msg['To'] = receiver

    smtp.sendmail(email, receiver, msg.as_string())
    smtp.quit()


def send_multipart_mail(receiver, subject, content):
    smtp = smtp_setting()

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = os.environ.get('GOOGLE_EMAIL')
    msg['To'] = receiver

    part1 = MIMEText(content['plain'], 'plain')
    part2 = MIMEText(content['html'], 'html')
    msg.attach(part1)
    msg.attach(part2)

    smtp.sendmail(email, receiver, msg.as_string())

    smtp.quit()
