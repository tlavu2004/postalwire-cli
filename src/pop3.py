import socket
import customed_socket as sk
import re
import os
import base64
import yaml
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

import email
from email import policy
from email.parser import BytesParser


class FileInfo:
    def __init__(self, name, _data):
        self.name = name
        self.encoded_data = _data

class Receivedmail:
    def __init__(self, msg_path):
        self.Id = os.path.basename(msg_path)
        with open(msg_path, 'r') as file:
            file_content=file.read()

            msg = BytesParser(policy=policy.default).parsebytes(file_content.encode('utf-8'))
            self.Sender = msg.get('From')
            self.Tos = msg.get('To')
            self.CCs = msg.get('CC')
            self.Subject = msg.get('Subject')
            self.Content = ""
            self.Attachments = []
            
            for part in msg.iter_parts():
                content_type = part.get_content_type()
                if 'text/plain' in content_type:
                    self.Content = part.get_payload()
                if 'application/octet-stream' in content_type:
                    # print(attachment_content.decode('utf-8'))
                    self.Attachments.append(FileInfo(part.get_filename(), part.get_payload()))
            file.close()

    def save_file(self, dir, index):
        if index < 0 or index >= len(self.Attachments):
            return False
        with open(f"{dir}/{self.Attachments[index].name}", "wb") as file:
            file.write(base64.b64decode(self.Attachments[index].encoded_data))
            file.close()
        return True

    def display(self):
        print(f"From: {self.Sender}")
        print(f"To: {self.Tos}")
        print(f"CC: {self.CCs}")
        print(f"Subject: {self.Subject}")
        print(f"Content: {self.Content}")


# -------------------------------------------------------------------- #

def classify_mail(mail, filters):
    # Load SMTP Configuration
    # with open('./Clone/Socket/src/config.yml', encoding='utf-8') as f:
    #     config = yaml.safe_load(f)
    # filters = config.get('Filter', [])
    for filter_rule in filters:
        criteria = filter_rule.get('Criteria')
        to_folder = filter_rule.get('To_folder')
        if criteria == 'From' and mail.Sender in filter_rule.get('Addresses', []):
            return to_folder
        elif criteria == 'Subject' and any(keyword.lower() in mail.Subject.lower() for keyword in filter_rule.get('Keywords', [])):
            return to_folder
        elif criteria == 'Content' and any(keyword.lower() in mail.Content.lower() for keyword in filter_rule.get('Keywords', [])):
            return to_folder
        elif criteria == 'Spam' and any(keyword.lower() in mail.Subject.lower() or keyword.lower() in mail.Content.lower() for keyword in filter_rule.get('Keywords', [])):
            return to_folder
    return 'Inbox'  # Default to 'Inbox' if no match

def update_mail_classification(user_dir, mail_id, classification):
    mail_classification_file = f"{user_dir}/MailClassification.yml"
    if not os.path.exists(mail_classification_file):
        with open(mail_classification_file, 'w') as f:
            f.write("")
    with open(mail_classification_file, 'a') as f:
        f.write(f"{mail_id}: {classification}\n")

# client_socket must be connected to the server before passing to the function
def receive_emails_from_server(client_socket: socket, user, password, user_dir, filters):
    # Receive the welcome message
    sk.recv(client_socket, 1)

    # Login
    sk.send(client_socket, f"USER {user}\r\n".encode())
    sk.recv(client_socket, 1)
    sk.send(client_socket, f"PASS {password}\r\n".encode())
    sk.recv(client_socket, 1)
    sk.send(client_socket, f"LIST\r\n".encode())
    size_list=sk.recv(client_socket, 1)
    mail_size=size_list.splitlines()
    mail_size=mail_size[1:-1]
    number_of_mails = len(mail_size)
    for i in range(number_of_mails):
        mail_size[i]=int(re.split(' ',mail_size[i])[1])
    
    sk.send(client_socket,"UIDL\r\n".encode())
    data = sk.recv(client_socket, 1)
    mailnames = data.splitlines()
    mailnames = mailnames[1:-1]
    for i in range(number_of_mails):
        mailnames[i] = re.split(' ', mailnames[i])[1]
    
    existing_msgs = set()
    for filename in os.listdir(user_dir):
        file_path = os.path.join(user_dir, filename)
        root, extension = os.path.splitext(file_path)
        if extension == '.msg':
            existing_msgs.add(filename)

    for i in range(number_of_mails):
        if mailnames[i] in existing_msgs:
            continue
        sk.send(client_socket,f"RETR {i+1}\r\n".encode())
        mail_str = sk.recv(client_socket, mail_size[i])

        mail_str = mail_str[mail_str.find('\n') + 1:]
        mail_str = mail_str.replace('\r', '')

        mail_path = f'{user_dir}/{mailnames[i]}'
        with open(mail_path, 'w') as file:
            file.write(mail_str)

        # Classify and update MailClassification.yml
        received_mail = Receivedmail(mail_path)
        classification = classify_mail(received_mail, filters)
        update_mail_classification(user_dir, mailnames[i], classification)
