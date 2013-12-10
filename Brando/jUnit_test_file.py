import DarkCloudCryptoLib as dcCryptoLib

##test Equal RSA keys
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
dcCryptoClient = dcCryptoLib.DCCryptoClient()
keyFileObj = dcCryptoClient.createKeyFileObj()

secureData = dcCryptoClient.encryptFile(plaintext, keyFileObj)
decryptedData = dcCryptoClient.decryptFile(secureData, keyFileObj)

print decryptedData == plaintext

secureKeyFile = keyFileObj.toSecureString()






