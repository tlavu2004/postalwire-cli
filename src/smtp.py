import socket
import customed_socket as sk
import os
import base64
import yaml
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

# Set the attachment size limit to 3MB
MAX_ATTACHMENT_SIZE = 3 * 1024 * 1024  # 3MB

class SentMail:
    def __init__(self, sender, tos, ccs, bccs, subject, content, attachments):
        self.sender = sender
        self.tos = tos
        self.ccs = ccs
        self.bccs = bccs
        self.subject = subject
        self.content = content
        self.attachments = attachments 

def send_email(client_socket:socket, mail : SentMail):
    
    # Receive the welcome message
    welcome_message = client_socket.recv(1024).decode()
    #print(welcome_message)

    # Login
    sk.send(client_socket, "EHLO localhost\r\n".encode())
    sk.recv(client_socket, 1)

    # Send mail data
    sk.send(client_socket,f"MAIL FROM: {mail.sender}\r\n".encode())
    sk.recv(client_socket, 1)

    all_recipients = mail.tos + mail.ccs + mail.bccs
    rcpt_commands = [f"RCPT TO: {recipient}\r\n" for recipient in all_recipients]

    for rcpt_command in rcpt_commands:
        sk.send(client_socket,rcpt_command.encode())
        sk.recv(client_socket, 1)


    sk.send(client_socket,"DATA\r\n".encode())
    sk.recv(client_socket, 1)

    # Construct and send the email
    msg = MIMEMultipart()
    msg['From'] = mail.sender
    msg['To'] = ', '.join(mail.tos)
    msg['CC'] = ', '.join(mail.ccs)
    msg['Subject'] = mail.subject
    msg.attach(MIMEText(mail.content, 'plain'))

    # file_path = 'path/to/your/file.txt'
    # attachment = MIMEBase('application', 'octet-stream')
    # attachment.set_payload(open(file_path, 'rb').read())
    # encoders.encode_base64(attachment)
    # attachment.add_header('Content-Disposition', f'attachment; filename="{file_path}"')
    # msg.attach(attachment)

    for attachment_path in mail.attachments:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attachment_path, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
        msg.attach(part)

        # with open(attachment_path, 'rb') as file:
        #     part = MIMEApplication(file.read(), Name=basename(attachment_path))
        #     part['Content-Disposition'] = f'attachment; filename="{basename(attachment_path)}"'
        #     msg.attach(part)

    sk.send(client_socket, msg.as_string().encode() + "\r\n".encode())

    # # Send attachments
    # for attachment_path in mail.attachments:
    #     with open(attachment_path, 'rb') as file:
    #         file_content = base64.b64encode(file.read())
    #         sk.send(client_socket , file_content)

    sk.send(client_socket, "\r\n.\r\n".encode())
    sk.recv(client_socket, 1)

    sk.send(client_socket,"QUIT\r\n".encode())

    print("Email sent successfully!")

