# Before you start you need to set imap permission from two accounts

# If you migrate the same mail address yandex and gmail do not delete 
# your account for a long time so feel free to create same mail address
# from gmail

import imaplib

# Account credentials
username_yandex = "mail@example.com"
# Password is not your password it is an app password from 2FA, if activated
password_yandex = "PASS"

username_gmail = "mail@example.com"
# Password is not your password it is an app password from 2FA, you need to activate
password_gmail = "PASS"

# If ssl connection is not an option
# Use imaplib.IMAP4("imap.xxx.com",PORT)

def reconnect_server(gmail,yandex,folder):
    gmail.abort()
    gmail = imaplib.IMAP4_SSL("imap.gmail.com")
    gmail.login(username_gmail,password_gmail)

    yandex.abort()
    yandex = imaplib.IMAP4_SSL("imap.yandex.com")
    yandex.login(username_yandex, password_yandex)
    yandex.select(folder)

def run_migration():
    # Not utf-8 format folders need to specify
    # If you want select from which folder to destination folder  
    folder_dict = {'Spam':'[Gmail]/Spam',
                   'Taslaklar':'[Gmail]/Taslaklar',
                   'Drafts':'[Gmail]/Taslaklar',
                   'INBOX':'INBOX'}
    # create an IMAP4 class with SSL 
    yandex = imaplib.IMAP4_SSL("imap.yandex.com")
    yandex.login(username_yandex, password_yandex)
    yandex_folder_list = yandex.list()[1]
    yandex_folder_list = yandex_folder_list[9:]
    gmail = imaplib.IMAP4_SSL("imap.gmail.com")
    gmail.login(username_gmail,password_gmail)
    for yandex_folder in yandex_folder_list:
        try:
            # Adapt yandex folder design to gmail folder format
            yandex_folder = yandex_folder.decode('utf-8').split('" ')[-1]
            # Gmail do not accept whitespace for this type of migration
            yandex_folder = yandex_folder.replace('"','').replace(" ","")
            status, messages = yandex.select(yandex_folder)
            # If interrupted, you can specify the folder and last email number then continue
            if yandex_folder == 'Folder':
                messages = 0
            else:
                messages = int(messages[0])
            # Adapt yandex folder design to gmail folder format
            if '|' in yandex_folder:
                yandex_folder = yandex_folder.replace('|','/')
            
            if yandex_folder in list(folder_dict.keys()):
                gmail_folder = folder_dict[yandex_folder]
            else:
                gmail.create('{}'.format(yandex_folder))
                gmail_folder = yandex_folder
            print('Started')
            for i in range(messages, 0, -1):
                try:
                    # If mail type is different in your region, change this data
                    data = yandex.fetch(str(i), "(FLAGS INTERNALDATE RFC822)")[1]
                    # There is a problem with the flags and if you run like below, all migrated emails will be opened on gmail
                    flags = imaplib.ParseFlags(data[0][0])
                    flag = ""
                    if flags != ():
                        for fl in flags:
                            flag = flag + ' ' + fl.decode('utf-8')
                            flag = flag.strip()
                    date = imaplib.Internaldate2tuple(data[0][0])
                    gmail.append(mailbox=gmail_folder, flags=flag, date_time=date, message=data[0][1])
                except Exception as e:
                    print(i,yandex_folder,gmail_folder,date,e)
                    reconnect_server(gmail,yandex,yandex_folder)
                print(i,yandex_folder,gmail_folder)
        except Exception as e:
            print(e)
            reconnect_server(gmail,yandex,yandex_folder)
    print('Finished')