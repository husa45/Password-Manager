#!/bin/python3
import hashlib
import getpass
#username :
username=input("enter the user name for the app\nusername: ")
#getting the original password with the salt :
passwd=getpass.getpass("set the password for the app\npassword: ")
salt=getpass.getpass("enter the salt (any word that you like\nused to increase security\nthe entered salt will be stored in the config files)\nsalt: ")
#calculating the hash of the password :
pwd_salted=passwd+salt
hash=hashlib.sha256(pwd_salted.encode()).hexdigest()
#writing the hash and the salt to the manager config file :
with open("/opt/tools/cyber_projects/passowrd_manager/configs/manager.confg","w") as appender:
	appender.write(f"salt value:{salt}\n")
	appender.write(f"Password hash:{hash}\n")
	appender.write(f"username:{username}\n")
	appender.write("salt path:/opt/tools/cyber_projects/passowrd_manager/configs/encryption_salt.txt")
