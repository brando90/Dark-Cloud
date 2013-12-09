import DarkCloudCryptoLib as dcCryptoLib
import os, random, struct, sys
import filecmp
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
import pbkdf2
import hashlib

##test lock and unlock functions work
tableKey = dcCryptoLib.DCTableKey('password', 'username', 'keyFilename')
plainText = "brando"
secureData = tableKey.lock(plainText)
decryptedData = tableKey.unlock(secureData)

print decryptedData == plainText
secureData = tableKey.lock(plainText)
decryptedData = tableKey.unlock(secureData)
print decryptedData == plainText
secureData = tableKey.lock(plainText)
decryptedData = tableKey.unlock(secureData)
print decryptedData == plainText

##test DCCryptoClient
#test keyFile
dcCryptoClient = dcCryptoLib.DCCryptoClient()
keyFileObj = dcCryptoClient.createKeyFileObj()

secureData = dcCryptoClient.encryptFile(plainText, keyFileObj)
decryptedData = dcCryptoClient.decryptFile(secureData, keyFileObj)

print decryptedData == plainText

#secureKeyFile = keyFileObj.toSecureString()

random_generator = Random.new().read
new_key = RSA.generate(1024, random_generator) #rsaObj 
public_key = new_key.publickey().exportKey("DER") 
private_key = new_key.exportKey("DER") 

pub_new_key = RSA.importKey(public_key)
pri_new_key = RSA.importKey(private_key)
pub_new_key = pub_new_key.exportKey("DER")
pri_new_key = pri_new_key.exportKey("DER")
print private_key == pri_new_key , public_key == pub_new_key





