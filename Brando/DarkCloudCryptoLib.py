import os, random, struct, sys
import filecmp
from Crypto.Cipher import AES
import pbkdf2
import hashlib

class DCKey:
    def __init__(self):
        pass

    def unlock(self, secureData):
        dcSignature = self.dcDecrypt(secureData)
        plaintext = self.dcVerify(dcSignature)
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
        index_signature = i + 1 + int(l)
        plainText = dcSignature[i+1:index_signature]
        rsaSignature = dcSignature[index_signature:]
        signature_to_verify = (long(rsaSignature), ) #tuple for rsa pycrypto should have (rsa_signature, )
        hash_val = hashlib.sha256(plain_text).digest()
        public_key = self.rsaKeyObj.publickey()
        if public_key.verify(hash_val, signature_to_verify):
            return plaintext
        else:
            raise ValueError("Verification failed")

class DCTableKey(DCKey):
    def __init__(self, username, password, keyFilename):
        #when making keys from password for a specific keyFilename
        salt = hashlib.sha256(username).digest()
        self.keyAES = makeKeyAES(password, salt)
        saltIv = str(hashlib.sha256(str(randStr)))
        self.iv = makeIV(self.keyAES, saltIv)
        self.rsaKeyObj = makeRSAKeyObj(password)


class DCFileKey(DCKey):
    def __init__(self, secureKeyFileData, keyObj):
        keyFileData = keyObj.unlock(secureKeyFileData)
        keysLengths = []
        commas = 0
        currentKeyLength = ""
        for i in range(0,keyFileData):
            c = keyFileData[i]
            if (c != ","):
                currentKeyLength+=c
            else:
                keysLengths.append(currentKeyLength)
                currentKeyLength = ""
                commas += 1
                if(commas == 3):
                    break
        ivLen = keysLengths[0]
        keyAESLen = keysLengths[1]
        rsaKeyObjLen = keysLengths[2]
        startKeyAES = i+1+ivLen
        self.iv = secureKeyFileData[i+1:startKeyAES]
        startRSAnum = startKeyAES+keyAESLen
        self.keyAES = secureKeyFileData[startKeyAES:startRSAnum]
        rsaRandNum = secureKeyFileData[startRSAnum:]
        self.rsaKeyObj = makeRSAKeyObj(rsaRandNum)

    def toSecureString(self, username, password, keyFileName):
        #generate keys
        iv = str(makeIV(os.urandom(32))) #size = 16
        keyAES = str(makeKeyAES(os.urandom(32))) #size = 32
        rsaRandNum = str(os.urandom(32)) # size = 32
        ivLen = len(iv)
        keyAESLen = len(keyAES)
        rsaRandNumLen = len(rsaRandNum)
        #generate plain text file data
        keyFileData = str(ivLen)+","+str(keyAESLen)+","+str(rsaRandNumLen)+","+iv+keyAES+rsaRandNum
        #generate secure file
        tableKey = DCTableKey(username, password, keyFilename)
        secureKeyTableFileData = tableKey.lock(keyFileData)
        return secureKeyTableFileData #string


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

    def createSecureKeyFile(self, username, password, keyFileName):
        #generate keys
        iv = str(makeIV(os.urandom(32))) #size = 16
        keyAES = str(makeKeyAES(os.urandom(32))) #size = 32
        rsaRandNum = str(os.urandom(32)) # size = 32
        ivLen = len(iv)
        keyAESLen = len(keyAES)
        rsaRandNumLen = len(rsaRandNum)
        #generate plain text file data
        keyFileData = str(ivLen)+","+str(keyAESLen)+","+str(rsaRandNumLen)+","+iv+keyAES+rsaRandNum
        #generate secure file
        tableKey = DCTableKey(username, password, keyFilename)
        secureKeyTableFileData = tableKey.lock(keyFileData)
        return secureKeyTableFileData #string


def encryptAES(keyAES, iv, plainText, mode = AES.MODE_CBC):
    encryptor = AES.new(keyAES, mode, iv)
    ciphertext = encryptor.encrypt(plainText)
    return ciphertext

def makeKeyAES(password, salt = os.urandom(32)):
        keyAES = pbkdf2.PBKDF2(str(password), str(salt)).read(32)
        return keyAES

def makeIV(key, salt = os.urandom(32)):
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


