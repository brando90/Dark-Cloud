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
        dcSignature = self.dcSign(plainText)
        secureData = self.dcEncript(dcSignature)
        return secureData

    def dcSign(self, plaintext):
        hashVal = hashlib.sha256(plainText).digest()
        (rsaSignature, nothin) = key.sign(hashVal, '')
        rsaSignature = str(rsaSignature)
        dcSignature = str(len(plainText))+ ","+ plainText + signature
        return dcSignature

    def dcEncrypt(self, dcSignature):
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
    def __init__(self, username, password, pathToKeyFilename):
        #when making keys from password for a specific keyFilename
        salt = hashlib.sha256(username).digest()
        self.keyAES = makeKeyAES(password, salt)
        saltIv = str(hashlib.sha256(str(keyFilename)))
        self.iv = makeIV(self.keyAES, saltIv)
        self.rsaKeyObj = makeRSAKeyObj(password)


class DCFileKey(DCKey):
    def __init__(self, iv, keyAES, rsaRandNum):
        self.keyAES = keyAES
        self.iv = iv
        self.rsaRandNum = rsaRandNum
        self.rsaKeyObj = makeRSAKeyObj(rsaRandNum)

    def toSecureString(self, username, password, pathToKeyFilename):
        #generate keys
        ivLen = len(self.iv)
        keyAESLen = len(self.keyAES)
        rsaRandNumLen = len(self.rsaRandNum)
        #generate plain text file data
        keyFileData = str(ivLen)+","+str(keyAESLen)+","+str(rsaRandNumLen)+","+self.iv+self.keyAES+self.rsaRandNum
        #generate secure file
        tableKey = DCTableKey(username, password, pathToKeyFilename)
        secureKeyTableFileData = tableKey.lock(keyFileData)
        return secureKeyTableFileData #string


class DCCryptoClient:
    def __init__(self):
        #maps name of file to its key object
        self.pathsToKeys = {}

    def addKeyObj(self, pathname, keyObj):
        #adds a key=name maping to value=keyObj to the dictionary
        self.pathsToKeys[pathname] = keyObj

    def encryptPath(self, wd):
        #"recursively" retur an encrypted path
        pass

    def getKey(self, pathname):
        return self.htKeys.get(pathname)

    def encryptName(self, name, keyObj):
        return keyObj.dcEncrypt(name) 

    def decryptName(self, encryptname, keyObj):
        return keyObj.dcDecrypt(encryptname)

    def encryptFile(self, fileContent, keyObj):
        return keyObj.lock(fileContent)

    def decryptFile(self, secureFileContent, keyObj):
        return keyObj.unlock(secureFileContent)

    def createKeyFileObj(self):
        #generate keys
        iv = str(makeIV(os.urandom(32))) #size = 16
        keyAES = str(makeKeyAES(os.urandom(32))) #size = 32
        rsaRandNum = str(os.urandom(32)) # size = 32
        keyFileObj = DCFileKey(iv, keyAES, rsaRandNum)
        return keyFileObj

    def makeKeyFileObjFromSecureKeyData(self, secureKeyFileData, username, password, keyFileName):
        keyObj = DCTableKey(username, password, keyFileName)
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
        iv = secureKeyFileData[i+1:startKeyAES]
        startRSAnum = startKeyAES+keyAESLen
        keyAES = secureKeyFileData[startKeyAES:startRSAnum]
        rsaRandNum = secureKeyFileData[startRSAnum:]
        keyFileObj = DCFileKey(iv, keyAES, rsaRandNum)
        return keyFileObj


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


