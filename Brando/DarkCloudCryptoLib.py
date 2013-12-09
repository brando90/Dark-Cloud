import os, random, struct, sys
import filecmp
from Crypto.Cipher import AES
import pbkdf2
import hashlib

class DCKey:
    def __init__(self):
        pass

    def unlock(self, secureData):

        return plainText

    def lock(self, plainText):
        dcSignature = self.makeDCsignature(plainText)
        secureData = self.makeDCEncryption(dcSignature)
        return secureData

    def makeDCSignature(self, plaintext):
        hashVal = hashlib.sha256(plainText).digest()
        (rsaSignature, nothin) = key.sign(hashVal, '')
        rsaSignature = str(rsaSignature)
        dcSignature = str(len(plainText))+ ","+ plainText + signature
        return dcSignature

    def makeDCEncryption(self, dcSignature):
        remainder = len(dcSignature) % 16
        amountPadding = 16 - remainder
        encryptor = AES.new(self.keyAES, AES.MODE_CBC, self.iv)
        if(amountPadding == 0):
            data = (" " * 15)+","+dcSignature
        else:
            data = (" " * amountPadding - 1)+","+dcSignature
        dcEncryptedData = encryptor.encrypt(data)
        return dcEncryptedData

    def dcDecrypt(self, secureData):
        decryptor = AES.new(self.keyAES, AES.MODE_CBC, self.iv)
        dcSignature = decryptor.decrypt(secureData)
        for i in range(0,len(dcSignature)):
            c = dcSignature[i]
            if c == ",":
                break
        return dcSignature[i+1:]

    def dcVerify(self, dcSignature):
        l = ""
        for i in range(0,len(dcSignature)):
            c = dcSignature[i]
            if c == ",":
                break
            l += c
        index_signature = i + 1 + l
        plainText = dcSignature[i:index_signature]
        rsaSignature = dcSignature[index_signature:]
        rsaSignature = long(rsaSignature)
        signature_to_verify = (rsaSignature, )
        hash_val = hashlib.sha256(plain_text).digest()
        if public_key.verify(hash_val, signature_to_verify):
            return plaintext
        else:
            return None




class DCTableKey(DCkey):
    __init__(self, password, username, keyFilename):
        #when making keys from password for a specific keyFilename
        salt = hashlib.sha256(username).digest()
        self.keyAES = makeKeyAES(password, salt)
        self.iv = makeIV(self.keyAES, keyFilename)
        self.rsaKeyObj = makeRSAKeyObj(password)


class DCFileKey(DCKey):
    __init__(self, ):
        pass

class DCCryptoClient:
    def __init__(self):
        #maps name of file to its key object
        self.htKeys = {}

    def addKeyObj(self, name, keyObj):
        #adds a key=name maping to value=keyObj to the dictionary
        pass

    def encryptPath(self, wd):
        #"recursively" retur an encrypted path
        pass

    def getKey(self, name):
        return self.htKeys[name]

    def encryptName(self, name, keyObj):
        #returns E[name, keyObj]
        pass

    def encryptKeyFileName(self, keyFileName, password):

        pass

    def encryptFile(self, fileContent, keyObj):
        pass

    def decryptFile(self, keyObj):
        pass

    def makeSecureKeyFile(self, username, password, keyFileName):
        #generate keys
        iv = makeIV(os.urandom(32)) #size = 16
        keyAES = makeKeyAES(os.urandom(32)) #size = 32
        rsaRandNum = os.urandom(32) # size = 32
        ivLen = len(iv)
        keyAES = len(keyAES)
        rsaRandNum = len(rsaRandNum)
        #generate plain text file data
        keyFileData = str(ivLen)+","+str(keyAES)+","+str(rsaRandNum)+","+str(iv)+str(keyAES)+str(rsaRandNum)
        #generate secure file
        tableKey = DCTableKey(password, username, keyFilename)
        secureKeyTableFileData = tableKey.lock(keyFileData)
        return secureKeyTableFileData #string


def encryptAES(keyAES, iv, plainText, mode = AES.MODE_CBC):
    encryptor = AES.new(keyAES, mode, iv)
    ciphertext = encryptor.encrypt(plainText)
    return ciphertext

def makeKeyAES(password, salt = os.urandom(32)):
        keyAES = pbkdf2.PBKDF2(str(password), str(salt)).read(32)
        return keyAES

def makeIV(key, randStr = os.urandom(32)):
    salt = str(hashlib.sha256(str(randStr)))
    iv = pbkdf2.PBKDF2(str(key), salt).read(16)
    return iv

def makeRSAKeyObj(password):
    key = RSA.generate(1024, random_generator)
    exportedKey = key.exportKey('DER', os.urandom(32), pkcs=1)
    key = RSA.importKey(exportedKey)
    return key


#keyFileData = DCCryptoClient().makeKeyFile("orochimaru" , "kitty")
#print keyFileData
tableKey = DCTableKey('password', 'username', 'keyFilename')
tableKey.lock("")


