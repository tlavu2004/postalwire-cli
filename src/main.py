import socket
import os
import yaml
import threading
import time
from os.path import basename

from smtp import *
from pop3 import *

# SMTP Configuration
with open('config.yml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

email_user = config['General']['Username']
email_pass = config['General']['Password']
mail_host = config['General']['MailServer']
smtp_port = config['General']['SMTP']
pop3_port = config['General']['POP3']
autoload = config['General']['Autoload']
mailbox = config['General']['Mailbox']

read_mail_dir = f"{mailbox}/{email_user}/ReadMails.yml"

# Set the attachment size limit to 3MB
MAX_ATTACHMENT_SIZE = 3 * 1024 * 1024  # 3MB

def menu_sendmail():
    #os.system("cls")
    tos = input("To (comma-separated): ").split(',')
    ccs = input("CC (comma-separated): ").split(',')
    bccs = input("BCC (comma-separated): ").split(',')
    subject = input("Subject: ")
    content = input("Content: ")
    attachments = []

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

    mail = SentMail(email_user, tos, ccs, bccs, subject, content, attachments)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((mail_host, smtp_port))
        print("Sending email...")
        send_email(client_socket, mail)
        print("Sending successfully")
         
def menu_receivemail():
    dir = f"{mailbox}/{email_user}"
    os.makedirs(dir, exist_ok=True)
    read_list = {}
    if  os.path.exists(read_mail_dir):
        with open(read_mail_dir) as f:
            read_list = yaml.safe_load(f)
    mails = []
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        root, extension = os.path.splitext(file_path)
        if extension == '.msg':
            mails.append(Receivedmail(file_path))
            if not filename in read_list:
                read_list[filename] = False
    
    print("Danh sách mail đã tải về:")
    for i in range(len(mails)):
        print(f"{i + 1}. <{mails[i].Sender}> - {mails[i].Subject} {"" if read_list[mails[i].Id] else "(*)"}")

    index = int(input("Chọn mail bạn muốn đọc: ")) - 1
    
    read_list[mails[index].Id] = True

    print("")
    mails[index].display()
    print("\nDanh sách các file trong mail ")
    for file in mails[index].Attachments:
        print(f"{file.name}")
    if not mails[index].Attachments:
        print("empty")

    if mails[index].Attachments:
        choice = input("Bạn có muốn lưu file không ? (Yes: 1, No: 0): ")
        if choice == '1':
            path=input("Nhập đường dẫn để lưu file : ")
            file_name=input("Nhập tên file muốn lưu : ")
            mails[index].save_file(path,file_name)

    print("")

    yaml_str = yaml.dump(read_list, default_flow_style=False)
    with open(read_mail_dir, 'w') as f:
        f.write(yaml_str)
            
g_is_running = True

def main_menu():
    global g_is_running
    while g_is_running:
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
            g_is_running = False
            print("Đã thoát chương trình. Hẹn gặp lại!")
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

def autoload_mails():
    global g_is_running

    user_dir = mailbox + '/' + email_user
    os.makedirs(user_dir, exist_ok=True)

    time_passed = 0.0

    prev = 0.0
    while g_is_running:
        current_time = time.time()
        time_passed += current_time - prev
        prev = current_time
        if (time_passed < autoload):
            continue
        time_passed = 0.0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((mail_host, pop3_port))
            receive_emails_from_server(client_socket, email_user, email_pass, user_dir)

def main():
    main_menu_thread = threading.Thread(target=main_menu)
    autoload_mails_thread = threading.Thread(target=autoload_mails)

    main_menu_thread.start()
    autoload_mails_thread.start()

    main_menu_thread.join()
    autoload_mails_thread.join()


if __name__ == "__main__":
    main()