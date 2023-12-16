import socket
import os
import base64
import yaml
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

# SMTP Configuration
with open('config.yml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

email_user = config['General']['Username']
email_pass = config['General']['Password']
mail_host = config['General']['MailServer']
smtp_mailserver = config['General']['SMTP']
pop3_mailserver = config['General']['POP3']
autoload = config['General']['Autoload']

# Set the attachment size limit to 3MB
MAX_ATTACHMENT_SIZE = 3 * 1024 * 1024  # 3MB

def send_email(to_addresses, cc_addresses, bcc_addresses, subject, content, attachments):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((mail_host, smtp_mailserver))

        # Receive the welcome message
        welcome_message = client_socket.recv(1024).decode()
        #print(welcome_message)

        # Login
        client_socket.sendall(b"EHLO localhost\r\n")
        client_socket.recv(1024)

        # Send mail data
        mail_from = f"MAIL FROM: {email_user}\r\n"
        client_socket.sendall(mail_from.encode())
        client_socket.recv(1024)

        all_recipients = to_addresses + cc_addresses + bcc_addresses
        rcpt_commands = [f"RCPT TO: {recipient}\r\n" for recipient in all_recipients]

        for rcpt_command in rcpt_commands:
            client_socket.sendall(rcpt_command.encode())
            client_socket.recv(1024)
    

        client_socket.sendall(b"DATA\r\n")
        client_socket.recv(1024)

        # Construct and send the email
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = ', '.join(to_addresses)
        msg['CC'] = ', '.join(cc_addresses)
        msg['BCC'] = ', '.join(bcc_addresses)
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))

        for attachment_path in attachments:
            with open(attachment_path, 'rb') as file:
                part = MIMEApplication(file.read(), Name=basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{basename(attachment_path)}"'
                msg.attach(part)

        client_socket.sendall(msg.as_string().encode() + b"\r\n")

        # Send attachments
        for attachment_path in attachments:
            with open(attachment_path, 'rb') as file:
                file_content = base64.b64encode(file.read())
                client_socket.sendall(file_content)

        client_socket.sendall(b"\r\n.\r\n")
        client_socket.recv(1024)

        client_socket.sendall(b"QUIT\r\n")
        client_socket.close()

    print("Email sent successfully!")
    # print("Email sent successfully! Press any key to return.")
    # input()

def send_individual_emails(addresses, subject, content, attachments):
    for address in addresses:
        send_email([], [], [address], subject, content, attachments)

def main_menu():
    while True:
        #os.system("cls")
        print("Vui lòng chọn Menu:")
        print("1. Để gửi email")
        print("2. Để xem danh sách các email đã nhận")
        print("3. Thoát")
        choice = input("Bạn chọn: ")

        if choice == '1':
            #os.system("cls")
            to_addresses = input("To (comma-separated): ").split(',')
            cc_addresses = input("CC (comma-separated): ").split(',')
            bcc_addresses = input("BCC (comma-separated): ").split(',')
            subject = input("Subject: ")
            content = input("Content: ")

            send_attachment = input("Include attachments? (1. Yes, 2. No): ")
            if send_attachment == '1':
                while True:
                    try:
                        num_attachments = int(input("Number of attachments: "))
                        break
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")

                attachments = []
                for i in range(num_attachments):
                    attachment_path = input(f"Enter path for attachment {i + 1}: ")
                    cont = True

                    while os.path.getsize(attachment_path) > MAX_ATTACHMENT_SIZE:
                        print(f"File '{attachment_path}' is too large (more than 3MB), do you want to resend?")
                        print("1. Yes")
                        print("2. No")
                        choose = int(input())

                        if (choose == 1):
                            attachment_path = input(f"Enter path for attachment {i + 1}: ")
                        elif (choose == 2):
                            cont = False
                            break
                        else:
                            print("Please choose again: ")
                    
                    if cont == True:
                        attachments.append(attachment_path.strip('"\''))

            else:
                attachments = []

            # Check if BCC has multiple addresses
            if len(bcc_addresses) > 1:
                send_individual_emails(bcc_addresses, subject, content, attachments)
            else:
                send_email(to_addresses, cc_addresses, bcc_addresses, subject, content, attachments)
         
        elif choice == '2':
            # Placeholder for viewing received emails (to be implemented)
            print("View received emails not implemented yet.")
        elif choice == '3':
            print("Đã thoát chương trình. Hẹn gặp lại!")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

if __name__ == "__main__":
    main_menu()