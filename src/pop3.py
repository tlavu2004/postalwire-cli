import socket
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


# SMTP Configuration
with open('config.yml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

email_user = config['General']['Username']
email_pass = config['General']['Password']
mail_host = config['General']['MailServer']
smtp_mailserver = config['General']['SMTP']
pop3_port = config['General']['POP3']
autoload = config['General']['Autoload']

class FileInfo:
    name: str
    encoded_data: str

class Receivedmail:
    Id : str
    Sender: str
    Tos = []
    CCs = []
    Subject : str
    Content : str
    Attachments = []

    def __init__(self, msg_path):
        self.Id = os.path.basename(msg_path)
        with open(msg_path,'r') as file:
            file_content=file.read()

            msg = BytesParser(policy=policy.default).parsebytes(file_content.encode('utf-8'))
            self.Sender = msg.get('From')
            self.Tos = msg.get('To')
            self.CCs = msg.get('CC')
            self.Subject = msg.get('Subject')
        
            for part in msg.iter_parts():
                content_type = part.get_content_type()
                if 'text/plain' in content_type:
                    self.Content = part.get_payload()
                if 'application/octet-stream' in content_type:
                    file_info = FileInfo()
                    file_info.name = part.get_filename()
                    file_info.encoded_data = part.get_payload()
                    # attachment_content = base64.b64decode(part.get_payload())
                    # print(attachment_content.decode('utf-8'))
                    self.Attachments.append(file_info)

    def save_file(self, dir, filename):
        for file_info in self.Attachments:
            if file_info.name != filename:
                continue
            with open(dir + '/' + filename, "wb") as file:
                file.write(base64.b64decode(file_info.encoded_data))
            break

    def display(self):
        print(f"From: {self.Sender}")
        print(f"To: {self.Tos}")
        print(f"CC: {self.CCs}")
        print(f"Subject: {self.Subject}")
        print(f"Content: {self.Content}")


def send(sender: socket, msg):
    sender.sendall((msg).encode())

def recv(receiver, size):
    res = ""
    while (len(res) < size):
        res += receiver.recv(3000000).decode()
    return res

def Receive_emails_from_server(user, password, path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((mail_host, pop3_port))

        # Receive the welcome message
        recv(client_socket, 1)

        # Login
        send(client_socket, f"USER {user}\r\n")
        recv(client_socket, 1)
        send(client_socket, f"PASS {password}\r\n")
        recv(client_socket, 1)
        send(client_socket, f"LIST\r\n")
        size_list=recv(client_socket, 1)
        mail_size=size_list.splitlines()
        mail_size=mail_size[1:-1]
        number_of_mails = len(mail_size)
        for i in range(number_of_mails):
            mail_size[i]=int(re.split(' ',mail_size[i])[1])
        
        send(client_socket,"UIDL\r\n")
        data=recv(client_socket, 1)
        mailnames=data.splitlines()
        mailnames=mailnames[1:-1]
        for i in range(number_of_mails):
            mailnames[i] = re.split(' ', mailnames[i])[1]
        
        for i in range(number_of_mails):
            send(client_socket,f"RETR {i+1}\r\n")
            mail=recv(client_socket, mail_size[i])

            mail=mail[mail.find('\n')+1:]
            mail=mail.replace('\r', '')
            with open(path+'/'+mailnames[i],'w') as file:
                file.write(mail)
        return mailnames



mailnames = Receive_emails_from_server("vy", "123", "msg")
print(mailnames)

maillist = []
for name in mailnames:
    mail = Receivedmail("msg/" + name)
    print(len(mail.Attachments))
    maillist.append(mail)


print("Mails:")
for i in range(len(maillist)):
    #print(f"{i + 1}. {maillist[i].Id}")
    print(f"number of att: {len(maillist[i].Attachments)}")



choice = int(input("Chon mail ban muon doc: ")) - 1

maillist[choice].display()

input = input("Input save dir: ")
for file_info in maillist[choice].Attachments:
    print(file_info.name)
    maillist[choice].save_file(input, file_info.name)
