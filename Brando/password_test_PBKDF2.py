import pbkdf2
from Crypto.Cipher import AES
import hashlib

salt = hashlib.sha256('username').digest()
keyAES = pbkdf2.PBKDF2("This passphrase is a secret.", salt).read(32) 
print len(keyAES)

iv = pbkdf2.PBKDF2(str(keyAES), str(hashlib.sha256("fileTableName"))).read(16)
print len(iv)

c = AES.new(keyAES, AES.MODE_CBC, iv)
