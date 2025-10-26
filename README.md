# Password Manager written in python

This is a full functional password manager written in python .

It consists of two main parts :

**1.Configure script :
Used to  set the credentials of the password manager like username ,password , and hashing salt.**


**2.Login page : A secure login using the username  and the password  set before .
It compares the entered password sha256 hash with the hash of the password set previously , if they match , and the username match , then access is granted , otherwise , error message is displayed.**

**3.Password manager page : The main module of the program , where you can store either a chosen password , or a random 21 character length 
generated password.
passwords are stored securely , encrypted with the fernet symmetric encryption algorithm , and the encryption key is derived from the login password at runtime , so , the key is not stored exciplicilty elsewhere (Which makes this password manager even more secure ).
You can also view the stored password , and delete it also if you want.**

 
**4.Password changing script :
used to securely change the old password , to the new password .**

**❗❗ Important Note :If the initial configuration script is used as a workaround to change the password , then the old passwords (which was encrypted using the key derived from the old password) ,You won`t be able to access them .
So the only way to change the password is using the  changing script provided (Which makes it secure by design).**

To download , first clone the repo to the destination place :

```
git clone  repo link
```

Install dependencies :
```
pip3 install -r requirements.txt
```

Then ,launch the configuration script :
```
python3 configure_script.py
```

To launch the password manager :
```
python3 password_manager.py
```
To change your password anytime ,    without losing access to old passwords : 
```
python3 password_change.py
```

 ## For any recommendations , contact me via my email :aljaarhussam2004@gmail.com

 
