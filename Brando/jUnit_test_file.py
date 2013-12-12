import DarkCloudCryptoLib as dcCryptoLib
from Crypto.PublicKey import RSA
import os

# ##test Equal RSA keys
rsaKey1 = dcCryptoLib.makeRSAKeyObj("password", "username")
rsaKey2 = dcCryptoLib.makeRSAKeyObj("password", "username")
print "equal RSA keys: ", dcCryptoLib.equalRSAKeys(rsaKey1, rsaKey2)

##test lock and unlock functions work
tableKey = dcCryptoLib.DCTableKey('password', 'username', 'keyFilename')
tableKeyCopy = dcCryptoLib.DCCryptoClient().createUserMasterKeyObj('password', 'username', 'keyFilename')
print "test: ",tableKey == tableKeyCopy

plaintext = "brando"

secureData = tableKey.lock(plaintext)
decryptedData = tableKey.unlock(secureData)
print "test1: ", decryptedData == plaintext
secureData = tableKey.lock(plaintext)
decryptedData2 = tableKey.unlock(secureData)
print "test2: ", decryptedData2 == plaintext
secureData = tableKey.lock(plaintext)
decryptedData3 = tableKey.unlock(secureData)
print "test3: ", decryptedData3 == plaintext

dcSignature = tableKey.dcSign(plaintext)
unSigned = tableKey.dcVerify(dcSignature)
print "test4: ", unSigned == plaintext

ciphertext = tableKey.dcEncript(plaintext)
decryptedData = tableKey.dcDecrypt(ciphertext)
print "test5: ", decryptedData == plaintext

secureData = tableKey.lock(plaintext)
sameTableKey = dcCryptoLib.DCTableKey('password', 'username', 'keyFilename')
decryptedData = sameTableKey.unlock(secureData)
print "test6: ", decryptedData == plaintext 

##test equality for keys
tableKey1 = dcCryptoLib.DCTableKey('password', 'username', 'keyFilename')
tableKey2 = dcCryptoLib.DCTableKey('password', 'username', 'keyFilename')
tableKey3 = dcCryptoLib.DCTableKey('password1', 'username', 'keyFilename')

print "table keys equal: ", tableKey1 == tableKey2
print "table testing not equality function: ", tableKey1 != tableKey3

##test DCCryptoClient
##test keyFile
plaintext = "brando"
dcCryptoClient = dcCryptoLib.DCCryptoClient()
keyFileObj = dcCryptoClient.createKeyFileObj()

secureData = dcCryptoClient.encryptFile(plaintext, keyFileObj)
decryptedData = dcCryptoClient.decryptFile(secureData, keyFileObj)

print "decrypting a secure file works: ", decryptedData == plaintext

secureKeyAsString = keyFileObj.toSecureString('password', 'username', 'keyFilename')
keyCopy = dcCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyAsString, 'password', 'username', 'keyFilename')

print "to Secure String works correctly: ", keyFileObj == keyCopy
# iv = "iv"
# keyAES = "keyAES"
# rsaRandNum = "rsaNum"
# print "=======Original origen======="
# print iv
# print keyAES
# print rsaRandNum
# print "======================"
keyF1 = keyFileObj
#print keyF1.toSecureString('password', 'username', 'keyFilename') == keyF2.toSecureString('password', 'username', 'keyFilename')
secureStr = keyF1.toSecureString('password', 'username', 'keyFilename')
keyMadeFromSecureString = dcCryptoClient.makeKeyFileObjFromSecureKeyData(secureStr, 'password', 'username', 'keyFilename')
# print "unlock secure string: ",dcCryptoLib.DCTableKey('password', 'username', 'keyFilename').unlock(secureStr)
print "was the key made from secure key match original: ",keyMadeFromSecureString == keyF1
# print "______keyObj______"
# print keyObj
# print "______keyF1______"
# print keyF1
secureData = dcCryptoClient.encryptFile(plaintext, keyMadeFromSecureString)
decryptedData = dcCryptoClient.decryptFile(secureData, keyF1)

print "decrypting a secure file works: ", decryptedData == plaintext

secureData = dcCryptoClient.encryptFile(plaintext, keyF1)
decryptedData = dcCryptoClient.decryptFile(secureData, keyMadeFromSecureString)

print "decrypting a secure file works: ", decryptedData == plaintext
print "do secure files match made by keys: ",keyF1.toSecureString('password', 'username', 'keyFilename') == keyMadeFromSecureString.toSecureString('password', 'username', 'keyFilename')

emptyStr = ""
secureData = tableKey.lock(emptyStr)
#print secureData
decryptedData = tableKey.unlock(secureData)
print "locking/unlocking a empty string works: ", decryptedData == emptyStr

######    ------------Sharing keys jUnit tests------------
password = "swordfish"   # for testing
salt = "yourAppName"     # replace with random salt if you can store one
key1 = dcCryptoLib.makeRSAKeyObj(password, salt)
key2 = dcCryptoLib.makeRSAKeyObj(password, salt)
print "keys equal: ", dcCryptoLib.equalRSAKeys(key1, key2)

#public_key = self.rsaKeyObj.publickey()
#self.rsaKeyObj.sign(hashVal, '')

#public keys equal
p = "123"
s = key1.sign(p , '')
si = (long(s[0]),)
pubKeyStr = key1.publickey().exportKey('PEM')
pubKeyCopy = RSA.importKey(pubKeyStr)
print "public keys equal: ", key1.publickey() == pubKeyCopy and key2.publickey() == pubKeyCopy

print "public keys equal: ", (key1 != pubKeyCopy) and (key2 != pubKeyCopy)
print "verify test: ", key1.publickey().verify(p, si)
print "verify test: ", pubKeyCopy.publickey().verify(p, si)

####======Sharing tests======
plaintext = "brando123"
dcCryptoClient = dcCryptoLib.DCCryptoClient()
keyFileObj = dcCryptoClient.createKeyFileObj()
readKey = dcCryptoClient.shareKeyFileAsRead(keyFileObj)

secureData = dcCryptoClient.encryptFile(plaintext, keyFileObj)
decryptedData = dcCryptoClient.decryptFile(secureData, readKey)

print "reading permission works 1: ", decryptedData == plaintext


secureReadKeyStr = readKey.toSecureString( "username", "password", "pathToKeyFilename")
readKeyFromStr = dcCryptoClient.makeKeyFileObjFromSecureKeyData( secureReadKeyStr, "username", "password", "pathToKeyFilename")
decryptedData2 = dcCryptoClient.decryptFile(secureData, readKeyFromStr)

print "reading from secure file worked: ", decryptedData2 == plaintext

##==
plaintext = "brando123"
dcCryptoClient = dcCryptoLib.DCCryptoClient()
keyFileObj = dcCryptoClient.createKeyFileObj()
name1 = dcCryptoClient.encryptName( "name", keyFileObj)
name2 = dcCryptoClient.encryptName( "name", keyFileObj)

print name1 == name2










