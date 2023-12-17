import socket
import os
import yaml
from os.path import basename

from smtp import *
from pop3 import *

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

def menu_sendmail():
    mail: SentMail
    #os.system("cls")
    mail.tos = input("To (comma-separated): ").split(',')
    mail.ccs = input("CC (comma-separated): ").split(',')
    mail.bccs = input("BCC (comma-separated): ").split(',')
    mail.subject = input("Subject: ")
    mail.content = input("Content: ")

    send_attachment = input("Include attachments? (1. Yes, 2. No): ")
    if send_attachment == '1':
        while True:
            try:
                num_attachments = int(input("Number of attachments: "))
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        mail.attachments = []
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
                mail.attachments.append(attachment_path.strip('"\''))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((mail_host, smtp_mailserver))
        print("Sending email...")
        send_email(client_socket, mail)
        print("Sending successfully")
         
def menu_receivemail():
    dir = input()

def main_menu():
    while True:
        #os.system("cls")
        print("Vui lòng chọn Menu:")
        print("1. Để gửi email")
        print("2. Để xem danh sách các email đã nhận")
        print("3. Thoát")
        choice = input("Bạn chọn: ")

        if choice == '1':
            menu_sendmail()
         
        elif choice == '2':
            menu_receivemail()
        elif choice == '3':
            print("Đã thoát chương trình. Hẹn gặp lại!")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

if __name__ == "__main__":
    main_menu()