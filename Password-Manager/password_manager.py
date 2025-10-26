import base64
import hashlib
import time
import random
import tkinter.ttk
from tkinter import messagebox, image_names, StringVar
import tkinter as tk
import cryptography as crypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
encryption_key:'bytes'=b'' #Note :this is not the fernet object , you need to generate it using : f=Fernet(key)
def generate_encryption_key(passwd: 'str',salt_path:'str') -> 'None':
    """generates the symmetric encryption key from the master password
    using fernets encryption + pseudo random key derivation function pbkdf2
    +a salt wich you need to store in other directory (specified in the config file)
    """
    salt,reader="",None
    #retrieving salt:
    try:
        reader=open(salt_path,'rb')
        salt=reader.read()
    except:
        print("ERRORRRR!!!")
        raise SystemExit()
    finally:
        reader.close()
    kdf=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=1_200_000)
    key = base64.urlsafe_b64encode(kdf.derive(passwd.encode()))  #key derived from master passwd , using pbkdf2
    #setting the global key:
    global encryption_key
    encryption_key=key
def encrypt_password(password:'str')->'bytes':
    """Encrypt the passed password , using the encryption key
    derived before .
    """
    f = Fernet(encryption_key)
    return f.encrypt(password.encode())
def decrypt_password(password:'bytes')->'str':
    f=Fernet(encryption_key)
    return f.decrypt(password).decode()
def read_passwords() ->'dict':
    file_content,result="",{}
    with open("passwords.encrypted","r") as r:
        file_content=r.read()
    if  not file_content: #reading the password file , while  it is empty
        print(file_content)
        return {}
    file_content=file_content.splitlines()
    for line in file_content:
        parts=line.split('-',maxsplit=2)
        result[parts[0]]={parts[1]:bytes(parts[2].replace("'","").replace("b","",1),encoding="utf-8")} #done this weird thing , because we read the file as text , not bytes
    return result
def hash_password(password:'str',hash_salt:'str')->'str':
    salted_pass:'str'=password+hash_salt
    return hashlib.sha256(salted_pass.encode()).hexdigest()
class  LoginGUI:
    """
    this class manages the login page , and the login process .
    """
    def __init__(self):
        #Main login window :
        self.window=tk.Tk()
        self.window.geometry("700x480")
        self.window.title("Login")
        self.window.resizable(False, False)
        #prevent the window from being closed by X .
        self.window.protocol("WM_DELETE_WINDOW",self.on_closing)
        #login page background :
        self.login_background = tk.PhotoImage(file='configs/background.png')
        background_label = tk.Label(master=self.window, image=self.login_background)
        background_label.place(relwidth=1, relheight=1)

        #window controls:

        self.login_button=tk.Button(master=self.window,text="Login",foreground="white",width=15,height=1,background="#003760",font=('Roman Times',10,"bold"),command=self.login_attempt)
        self.username=tk.Entry(width=35,bg="#F7F0F0",font=('Roman Times',10,"bold"))
        self.password=tk.Entry(width=35,bg="#F7F0F0",font=('Roman Times',10,"bold"))
        self.lab1=tk.Label(master=self.window,text="Username :",background="#02111F",fg="white",font=('Roman Times',10,"bold"))
        self.lab2 = tk.Label(master=self.window,text="Password: ",background="#02111F",fg="white",font=('Roman Times',10,"bold"))
        #placing controls at their respective place :
        self.username.place(x=320,y=200)
        self.password.place(x=320,y=275)
        self.lab1.place(x=195,y=200)
        self.lab2.place(x=195,y=275)
        self.login_button.place( x=480,y=320)
        #start:
        self.window.mainloop()
    def login_attempt(self):
        """Function invoked when the login button is pressed"""
        username=self.username.get().strip()
        passwd=self.password.get().strip()
        #getting the credentials from the config file , for authentication
        original_username:'str'=None
        password_hash:'str'=None
        hash_salt:'str'=None
        with open("/opt/tools/cyber_projects/passowrd_manager/configs/manager.confg","r") as reader:
            while (line:=reader.readline()):
                if line.startswith("username"):
                    original_username=line.split(':')[1].strip('\n')
                elif line.startswith("Password hash"):
                    password_hash = line.split(':')[1].strip('\n')
                elif line.startswith("salt value"):
                     hash_salt= line.split(':')[1].strip('\n')
        if username==original_username and hash_password(passwd,hash_salt)==password_hash:
            messagebox.showinfo(title="Successful !!!",message="Successful authentication\n           Welcome")
            #retrievign the salt path from the config:
            salt_path:'str'=""
            with open('configs/manager.confg','r') as r:
                for line in r.readlines():
                    if line.startswith('salt path'):
                        salt_path=line.strip('\n').split(':')[1]
                        break
            generate_encryption_key(passwd,salt_path)
            #close the login page:
            self.window.destroy()
        else:
            messagebox.showerror(title="Failed !!!",message="The username or password that you provided\nis incorrect , try again")
    def disable_event(self)->'None':

        pass
    def on_closing(self)->'None':
        """
        Action invoked when trying to close the window
        """
        if messagebox.askyesno(title="Quit",message="Are you sure that you want to quit?"):
            self.window.destroy()
            #if this is not done , it will progress to the manager window
            raise SystemExit()
class PassManager:
    """
    This is the class that manages the password manager , and all of it`s functionality
    """
    def __init__(self):
        self.requested_info=None
        #defining the programs window

        self.window = tk.Tk()
        self.window.title("Password Manager")
        self.window.geometry("700x480")
        self.window.resizable(False,False)
        self.window.protocol("WM_DELETE_WINDOW",self.on_closing)

        # Load the background image

        self.login_background = tk.PhotoImage(file='configs/background.png')
        background_label = tk.Label(master=self.window, image=self.login_background)
        background_label.place(relwidth=1, relheight=1)

        #Password manager interface

        self.pass_gen_box=tk.Entry(master=self.window,width=24,bg="#F7F0F0",relief="raised",font=('Roman Times',10,"bold"))
        self.pass_gen_button=tk.Button(master=self.window,text="generate password",foreground="white",width=15,height=1,background="#003760",font=('Roman Times',10,"bold"),command=self.generate_random_password)
        self.pass_ask_label=tk.Label(master=self.window,text="Password: ",background="#02111F",fg="white",font=('Roman Times',10,"bold"))
        self.add_pass_button=tk.Button(master=self.window,text="ADD",background="#003760",foreground="white",width=49,height=1,font=('Roman Times',10,"bold"),command=self.add_password)
        self.username_label=tk.Label(master=self.window,text="Email/Username:",background="#02111F",fg="white",font=('Roman Times',10,"bold"))
        self.username_entry=tk.Entry(master=self.window,width=37,bg="#F7F0F0",relief="raised",font=('Roman Times',10,"bold"))
        self.website_name_label=tk.Label(master=self.window,text="Website name: ",background="#02111F",fg="white",font=('Roman Times',10,"bold"))
        self.website_name_entry = tk.Entry(master=self.window, width=19, bg="#F7F0F0",relief="raised",font=('Roman Times',10,"bold"))
        #passwords drop down list:

        self.password_parts:'dict'=read_passwords()
        self.droplist=tkinter.ttk.Combobox(master=self.window,justify="left",state="normal",font=('Roman Times',10,"bold"),values=list(self.password_parts.keys()))
        self.droplist.set("click to see passwords ")
        self.droplist.bind("<<ComboboxSelected>>",self.get_password)
        self.droplist.place(x=350,y=10)

        #place controls at their respective locations :
        self.add_pass_button.place(x=225,y=380)
        self.pass_gen_box.place(x=300,y=320)
        self.pass_gen_button.place(x=530,y=320)
        self.pass_ask_label.place( x=200,y=320)
        self.username_label.place(x=200, y=260)
        self.username_entry.place(x=350,y=260)
        self.website_name_label.place(x=200,y=200)
        self.website_name_entry.place(x=350,y=200)
        #start :
        self.window.mainloop()
    def generate_random_password(self) ->'None':
        """
        Generate a random password of length 21
        """
        #delete the previously generated one:
        self.pass_gen_box.delete('0',tk.END)
        allowed_characters=['a','b','c','d','e','f','g','h','i','j','k','l','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9','!','#','$','%','&','*','+',',','-','/','=','?','@','[','\\',']','^','_','{','|','}','~']
        random_pass=""
        for i in range(1,21):
            random_pass+=allowed_characters[random.randint(0,82)]
        self.pass_gen_box.insert(index='0',string=random_pass)
    def add_password(self) ->'None':
        """
        This function adds the password , with its related info
        to the passwords.encrpyted file in the program`s working directory

        The password follows the current form:
        website name-email/username-encrypted password
        """
        global encryption_key
        website_name:'str'=self.website_name_entry.get()
        username:'str'=self.username_entry.get()
        password:'str'=self.pass_gen_box.get()
        if website_name and username and password :
            with open('passwords.encrypted','a') as w:
                encrypted_pass=encrypt_password(password)
                #writing the passowrd strcuture:
                w.write(f"{website_name}-{username}-{encrypted_pass}\n")
                #update the password menu :
                self.on_add(website_name)
            #read the file ,after closing it :
            self.password_parts: 'dict' = read_passwords()
            messagebox.showinfo(title="Adding succeeded",message="The password was added successfully !!!\n")
            self.clear_entries()
        else:
            messagebox.showerror(title="Cant write password!!!",message=f"All fields must be entered\n\n")
    def get_password(self,event=None)  ->'None':
        """This function retrieves the password
        according to the name of the button that is pressed in the drop down-list
        """
        website_name=self.droplist.get()
        username=list(self.password_parts[website_name].keys())[0]
        self.display_password(website_name,username,password=decrypt_password(self.password_parts[website_name][username]))
    def display_password(self,website_name:'str',username:'str',password:'str') ->'None':
        """
        This function is invoked , when the user wants to view the stored password
        from the list.
        """
        password_popup = tk.Tk()
        password_popup.title("Requested password")
        password_popup.geometry("700x150")
        password_popup.resizable(False,False)
        self.requested_info=tk.Text(master=password_popup,height=5,wrap='none',borderwidth=0,highlightthickness=0,cursor="xterm",font=("Roman Times",11,"bold"))
        self.requested_info.insert("1.0",f"Website name : {website_name}\n\nUsername/Email :  {username}\n\nPassword :  {password}\n")
        delete_pass_button=tk.Button(master=password_popup,text="delete password",font=("Roman Times",11,"bold"),command=self.on_remove)
        delete_pass_button.pack(side=tk.BOTTOM)
        self.requested_info.pack()
        password_popup.mainloop()
    def on_remove(self)->'None':
        """
        This function effectively removes the password when the button is clicked
        """
        to_remove:'str'=(self.requested_info.get("1.0",tk.END).split('\n')[0]).split(':')[1].strip()
        current_options = list(self.droplist['values'])
        try:
            current_options.remove(to_remove)
        except ValueError:
            messagebox.showerror(title="Error",message="The password you are trying to delete is not found\n")
            return
        #deleting the password from the file:
        lines:'list'=[]
        with open('passwords.encrypted','r') as reader:
            lines=reader.readlines()
        with open('passwords.encrypted','w') as writer:
            for line in lines:
                if line.startswith(to_remove):
                    continue
                writer.write(line)
        self.droplist['values']=current_options
    def on_add(self,new_entry:'str')->'None':
        """
        update the password menu whenever a password is added .
        """
        current_options=list(self.droplist['values'])
        current_options.append(new_entry)
        self.droplist['values']=current_options
    def clear_entries(self)->'None':
        self.username_entry.delete(0,tk.END)
        self.pass_gen_box.delete(0,tk.END)
        self.website_name_entry.delete(0,tk.END)
    def on_closing(self)->'None':
        if messagebox.askyesno(title="Quit?",message="Do you want to quit?"):
            self.window.destroy()
gui=LoginGUI()
manager=PassManager()