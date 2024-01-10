import socket
import os
import yaml
import threading
import time
import shutil
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
filters = config.get('Filter', [])

user_dir = f"{mailbox}/{email_user}"
read_mail_path = f"{user_dir}/ReadMails.yml"

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

    send_attachment = input("Bạn có muốn thêm file đính kèm không? (1. Yes, 0. No): ")
    if send_attachment == '1':
        while True:
            try:
                num_attachments = int(input("Số lượng file đính kèm: "))
                break
            except ValueError:
                print("Đầu vào không hợp lệ. Vui lòng nhập số hợp lệ khác.")

        attachments = []
        for i in range(num_attachments):
            attachment_path = ""
            while True:
                attachment_path = input(f"Nhập đường dẫn file {i + 1}: ")
                cont = True
                if (os.path.exists(attachment_path)):
                    break

            while os.path.getsize(attachment_path) > MAX_ATTACHMENT_SIZE:
                print(f"File '{attachment_path}' quá lớn (hơn 3 MB), bạn có muốn gửi lại không?")
                print("1. Yes") 
                print("2. No")
                choose = int(input())

                if (choose == 1):
                    attachment_path = input(f"Nhập đường dẫn file {i + 1}: ")
                elif (choose == 2):
                    cont = False
                    break
                else:
                    print("Vui lòng chọn lại: ")
            
            if cont == True:
                attachments.append(attachment_path.strip('"\''))

    mail = SentMail(email_user, tos, ccs, bccs, subject, content, attachments)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((mail_host, smtp_port))
        print("Đang gửi email...")
        send_email(client_socket, mail)
        print("Gửi email thành công ")

def menu_receivemail():
    menu_receivemail_is_running = True
    while menu_receivemail_is_running:
        back = False
        while True:
            print("Đây là danh sách các folder trong mailbox của bạn:")
            print("1. Inbox")
            print("2. Project")
            print("3. Important")
            print("4. Work")
            print("5. Spam")
            choose = input("Bạn muốn xem email trong folder nào (Nhấn Enter để quay lại): ")
            if not choose:
                back = True
                break
            elif '1' <= choose <= '5':
                choose = int(choose) - 1
                break
            else:
                print("Vui lòng nhập lại:")

        if back == True:
            return

        chosen_folder = ["Inbox", "Project", "Important", "Work", "Spam"][choose]

        with open(f'{user_dir}/MailClassification.yml', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        read_list = {}
        if os.path.exists(read_mail_path):
            with open(read_mail_path) as f:
                read_list = yaml.safe_load(f)

        classify_mails = []
        for filename in os.listdir(user_dir):
            file_path = os.path.join(user_dir, filename)
            root, extension = os.path.splitext(file_path)
            if extension != '.msg':
                continue

            for key, value in data.items():
                if key == filename and value == chosen_folder:
                    classify_mails.append(Receivedmail(file_path))

            if not filename in read_list:
                read_list[filename] = False

        if len(classify_mails) == 0:
            print(f"Không có email trong {chosen_folder} folder")
            input()
            break

        print(f"Đây là danh sách email trong {chosen_folder} folder:")
        for i in range(len(classify_mails)):
            print(f"{i + 1}. {"" if read_list[classify_mails[i].Id] else "(chưa đọc) "}<{classify_mails[i].Sender}> - {classify_mails[i].Subject}")

        index = int(input("Chọn mail bạn muốn đọc (Chọn 0 để quay lại): "))
        index -= 1
        chosen_mail = classify_mails[index]

        if index == -1:
            continue

        menu_receivemail_is_running = False

        read_list[chosen_mail.Id] = True

        print("")
        chosen_mail.display()
        print("\nDanh sách các file trong mail ")
        if not chosen_mail.Attachments:
            print("empty")
        for i in range(len(chosen_mail.Attachments)):
            print(f"{i+1}. {chosen_mail.Attachments[i].name}")

        if chosen_mail.Attachments:
            choice = input("Bạn có muốn lưu file không ? (Yes: 1, No: 0): ")
            if choice == '1':
                path = input("Nhập đường dẫn để lưu file : ")
                index = int(input("Nhập thứ tự file muốn lưu : ")) - 1
                if chosen_mail.save_file(path, index):
                    print("Lưu file thành công!")
                else:
                    print("Không thể lưu file!")

        print("")

        yaml_str = yaml.dump(read_list, default_flow_style=False)
        with open(read_mail_path, 'w') as f:
            f.write(yaml_str)
        f.close()

        # # --- #
        # folder_path = f"{user_dir}/MailBox/{chosen_folder}"
        # if not os.path.exists(folder_path):
        #     os.makedirs(folder_path)

        # # Combine the folder path and source file name
        # source_file = f'{user_dir}/{chosen_mail.Id}'
        # destination_file = os.path.join(folder_path, chosen_mail.Id)

        # # Copy the file to the destination folder
        # shutil.copy(source_file, destination_file)
            
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
            receive_emails_from_server(client_socket, email_user, email_pass, user_dir, filters)

def main():
    os.makedirs(user_dir, exist_ok=True)

    main_menu_thread = threading.Thread(target=main_menu)
    autoload_mails_thread = threading.Thread(target=autoload_mails)

    main_menu_thread.start()
    autoload_mails_thread.start()

    main_menu_thread.join()
    autoload_mails_thread.join()


if __name__ == "__main__":
    main()