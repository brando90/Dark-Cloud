import DarkCloudCryptoLib as dcCryptoLib
import os

# ##test Equal RSA keys
rsaKey1 = dcCryptoLib.makeRSAKeyObj("password", "username")
rsaKey2 = dcCryptoLib.makeRSAKeyObj("password", "username")
print "equal RSA keys: ", dcCryptoLib.equalRSAKeys(rsaKey1, rsaKey2)

##test lock and unlock functions work
tableKey = dcCryptoLib.DCTableKey('password', 'username', 'keyFilename')
plaintext = "brando"

secureData = tableKey.lock(plaintext)
decryptedData = tableKey.unlock(secureData)
print "test1: ", decryptedData == plaintext
secureData = tableKey.lock(plaintext)
decryptedData = tableKey.unlock(secureData)
print "test2: ", decryptedData == plaintext
secureData = tableKey.lock(plaintext)
decryptedData = tableKey.unlock(secureData)
print "test3: ", decryptedData == plaintext

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





