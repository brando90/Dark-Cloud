from Crypto.PublicKey import RSA
from Crypto import Random
import hashlib

print "<----------RSA TESTING STARTING---------->\n"
fileTableName = "fileTableName"
username = "orochimaru"
password = "kitty"
plain_text = "abcdefgh"

random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
exportedKey = key.exportKey('PEM', password, pkcs=1)
key = RSA.importKey(exportedKey, password)
public_key = key.publickey()

##Some methods of keys
print "can_encrypt: ", key.can_encrypt()
print "can_sign: ", key.can_sign()
print "has_private: ", key.has_private()

#SIGNING
hash_val = hashlib.sha256(plain_text).digest()
signature = key.sign(hash_val, '')
print signature
#print "signature: ",signature

print "<----------AES-CBC TEST STARTING---------->\n"
import pbkdf2
from Crypto.Cipher import AES
import hashlib

salt = hashlib.sha256(username).digest()
keyAES = pbkdf2.PBKDF2(password, salt).read(32) 
iv = pbkdf2.PBKDF2(str(keyAES), str(hashlib.sha256(fileTableName))).read(16)

encryptor = AES.new(keyAES, AES.MODE_CBC, iv)
decryptor = AES.new(keyAES, AES.MODE_CBC, iv)

ciphertext = encryptor.encrypt(str(signature[0]))

#VERIFYING
print "Verfification result: ", public_key.verify(hash_val, (decryptor.decrypt(ciphertext),))

