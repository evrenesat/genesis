# -*-  coding: utf-8 -*-
"""
"""
import smtplib

from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import os
from lab.models import Admission

FROM_MAIL = os.getenv('MAIL_LOGIN')

try:
    from weasyprint import HTML
except ImportError:
    HTML = None

def send_mail(subject, body, to, files=None, file_paths=None):
    """
    sends an email with attaching given files (file contents or file paths)

    :param file_paths:
    :param subject:
    :param body:
    :param to:
    :param files:
    :return:
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = FROM_MAIL
    msg['To'] = to
    msg.preamble = body

    if files:
        for file in files:
            msg.attach(MIMEApplication(file))

    if file_paths:
        for file in file_paths:
            with open(file, 'rb') as fp:
                msg.attach(MIMEApplication(fp.read()))

    # Send the email via our own SMTP server.
    # s = smtplib.SMTP('localhost')
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(FROM_MAIL, os.getenv('MAIL_KEY'))
    server.send_message(msg)
    server.quit()


def send_analyse_report(admission_id):
    admission = Admission.objects.get(pk=admission_id)


