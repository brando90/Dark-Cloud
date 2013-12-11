from Crypto.PublicKey import RSA
from Crypto import Random
import DarkCloudCryptoLib as dcCryptoLib

import hashlib
import sys
import os

#comparing RSA keys
# random_generator = Random.new().read
# new_key = RSA.generate(1024, random_generator) #rsaObj 
# public_key = new_key.publickey().exportKey("DER") 
# private_key = new_key.exportKey("DER") 

# pub_new_key = RSA.importKey(public_key)
# pri_new_key = RSA.importKey(private_key)
# pub_new_key = pub_new_key.exportKey("DER")
# pri_new_key = pri_new_key.exportKey("DER")
# print private_key == pri_new_key , public_key == pub_new_key
password = "password"

new_key1 = RSA.generate(1024, lambda n: (chr(0)*(n-1))+chr(1) ) #rsaObj
exportedKey1 = new_key1.exportKey('DER', password, pkcs=1)
key1 = RSA.importKey(exportedKey1)

new_key2 = RSA.generate(1024, lambda n: (chr(0)*(n-1))+chr(1) ) #rsaObj
exportedKey2 = new_key2.exportKey('DER', password, pkcs=1)
key2 = RSA.importKey(exportedKey2)
print dcCryptoLib.equalRSAKeys(key1, key2)