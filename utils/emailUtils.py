import smtplib
from email import encoders
from email.utils import COMMASPACE, formatdate
from email.mime.multipart import MIMEMultipart
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText


def sendEmail(Params, bcc=False, html=None):
    recipients = Params["recipients"]
    fromaddr = Params["fromAddress"]
    subject = Params["subject"]
    message = Params["message"]
    server = "smtp-central.internal.ericsson.com"
    port = 25


    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = COMMASPACE.join(recipients)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    if html:
        msg.attach( MIMEText(message, html) )
    else:
        msg.attach( MIMEText(message) )

    validateSendEmailParams(Params)
    if "attachmentfile" in Params.keys():
        attachmentfile = Params["attachmentfile"]
        attachmentname = Params["attachmentname"] if "attachmentname" in Params.keys() else "okta-attachment.xlsx"
        part = MIMEBase('application', "octet-stream")
        part.set_payload(attachmentfile ,'vnd.ms-excel')
        part.add_header('Content-Disposition', 'attachment', filename=attachmentname)
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if bcc:
        recipients = Params['bcc_recipients']
        recipients = COMMASPACE.join(recipients)
        smtp.sendmail(fromaddr, recipients, msg.as_string())
    else:
        smtp.sendmail(fromaddr, recipients, msg.as_string())

    smtp.close()

    return True

def validateSendEmailParams(Params):
    return True