from PBKDF2 import PBKDF2
from Crypto.Cipher import AES
import hashlib

salt = hashlib.sha256('username').digest()
key = PBKDF2("This passphrase is a secret.", salt).read(32) 
print len(key)
iv = hashlib.sha256('username').digest() 
print(key)
cipher = AES.new(key, AES.MODE_CBC, iv)