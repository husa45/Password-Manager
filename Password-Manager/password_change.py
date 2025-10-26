#!/bin/python3
import getpass
import hashlib
import base64
import tkinter as tk
from tkinter import messagebox
import cryptography as crypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
#edfdfs-sdfsdf-b'gAAAAABo_NBTbyfLqRKkty0W607IaaO_1V_gS8hrWrmMh4kty3s4qINhfbkFJubOB--h5hetQGLEA9WqTqRwR-oGVmfDxQaQ_LnPX-qjPl2-73cGEiafbTU='

def decrypt(passwd:'bytes',key) ->'bytes':
    f=Fernet(key)
    return f.decrypt(passwd)
def encrypt(passwd:'bytes',key)->'bytes':
    f=Fernet(key)
    return f.encrypt(passwd)
def hash_password(password:'str',hash_salt:'str')->'str':
    salted_pass:'str'=password+hash_salt
    return hashlib.sha256(salted_pass.encode()).hexdigest()
def change_stored_hash(passwd:'str'):
    lines=[]
    with open ("configs/manager.confg","r") as reader:
        lines=reader.readlines()
    new_hash=hashlib.sha256((passwd+lines[0].strip("\n").split(':')[1]).encode()).hexdigest()
    with open("configs/manager.confg","w") as writer:
        for line in lines:
            if line.startswith("Password hash"):
                writer.write(f"Password hash:{new_hash}\n")
                continue
            writer.write(line)
def re_encrypt(old_passwd:'str',new_passwd:'str',salt_path:'str') ->'None':
    """
    This function is supposed to read passwords encrypted with the old key (which was generated from the old password)
    and rencrypt them with the key generated from the new master password
    """
    #genrating the old key , and the new key :
    salt, reader = "", None
    # retrieving salt:
    try:
        reader = open(salt_path, 'rb')
        salt = reader.read()
    except:
        print("ERRORRRR!!!")
        raise SystemExit()
    finally:
        reader.close()
    kdf1=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=1_200_000)
    kdf2= PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=1_200_000)
    key1 = base64.urlsafe_b64encode(kdf1.derive(old_passwd.encode())) #old passwd key
    key2 = base64.urlsafe_b64encode(kdf2.derive(new_passwd.encode())) #new passwd key

    #rencrypting the file with the new key :
    lines=[]
    with open("passwords.encrypted","r") as reader:
        lines=reader.readlines()
    with open("passwords.encrypted","w") as writer:
        for line in lines:
            parts:'list'=line.split('-',maxsplit=2)
            website_name,username=parts[0],parts[1]
            encrypted_password=bytes(parts[2].replace("'","").replace("b","",1),encoding="utf-8")
            #rencrypt it with the new key :
            encrypted_password=encrypt(decrypt(encrypted_password,key1),key2)
            writer.write(f"{website_name}-{username}-{encrypted_password}\n")
class ChangePassword :
    """
    This class handles password changing behaviour
    """
    def __init__(self):
        # Main login window :
        self.window = tk.Tk()
        self.window.geometry("700x480")
        self.window.title("Login")
        self.window.resizable(False, False)
        # prevent the window from being closed by X .
        self.window.protocol("WM_DELETE_WINDOW",self.on_closing)
        # login page background :
        self.login_background = tk.PhotoImage(file='configs/background.png')
        background_label = tk.Label(master=self.window, image=self.login_background)
        background_label.place(relwidth=1, relheight=1)

        #Window layout :
        self.old_pass_entry=tk.Entry(master=self.window,width=30,bg="#F7F0F0",font=('Roman Times',10,"bold"))
        self.old_pass_label=tk.Label(master=self.window,text="Old password :",background="#02111F",fg="white",font=('Roman Times',10,"bold"))
        self.new_password_entry=tk.Entry(master=self.window,width=30,bg="#F7F0F0",font=('Roman Times',10,"bold"))
        self.new_pass_label = tk.Label(master=self.window, text="New password :", background="#02111F", fg="white",
                                       font=('Roman Times', 10, "bold"))
        self.change_password_button=tk.Button(master=self.window,text="Change",width=13,height=1,foreground="white",background="#003760",font=('Roman Times',10,"bold"),command=self.change_pass)

        #place controls at respective place :
        self.change_password_button.place(x=470,y=250)
        self.old_pass_entry.place(x=340, y=130)
        self.old_pass_label.place(x=200,y=130)
        self.new_password_entry.place(x=340,y=190)
        self.new_pass_label.place(x=200,y=190)
        #start the app :
        self.window.mainloop()
    def change_pass(self)->'None':
        old_passwd = self.old_pass_entry.get().strip()
        new_passwd = self.new_password_entry.get().strip()

        #getting the old credentials :
        password_hash: 'str' = None
        hash_salt: 'str' = None
        salt_path:'str'=None
        with open("configs/manager.confg","r") as reader:
            while (line:=reader.readline()):
               if line.startswith("Password hash"):
                    password_hash = line.split(':')[1].strip('\n')
               elif line.startswith("salt value"):
                     hash_salt= line.split(':')[1].strip('\n')
               elif line.startswith("salt path"):
                   salt_path = line.split(':')[1].strip('\n')
        if hash_password(old_passwd,hash_salt)==password_hash:
            re_encrypt(old_passwd,new_passwd,salt_path)
            change_stored_hash(new_passwd)
            messagebox.showinfo(title="Successful !!!",message="Password changed successfully")
        else:
            messagebox.showerror(title="Error !!!",message="Incorrect old password\nTry again !!!")
    def on_closing(self)->'None':
        """
        Action invoked when trying to close the window
        """
        if messagebox.askyesno(title="Quit",message="Are you sure that you want to quit?"):
            self.window.destroy()
            #if this is not done , it will progress to the manager window
            raise SystemExit()
ChangePassword()




