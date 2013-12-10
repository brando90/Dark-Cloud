import os, random, struct, sys
import filecmp
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
import pbkdf2
import hashlib

class DCKey:
    def __init__(self):
        pass

    def __str__(self):
        s="----DCKey print----\n"
        s+="----\n"
        s+="iv: "+self.iv+"\n"
        s+="----\n"+"\n"
        s+="keyAES: "+self.keyAES+"\n"
        s+="----\n"
        s+="RSAObj: "+str(self.rsaKeyObj)+"\n"
        s+="----\n"
        return s

    def unlock(self, secureData):
        dcSignature = self.dcDecrypt(secureData)
        plaintext = self.dcVerify(dcSignature)
        return plaintext

    def lock(self, plaintext):
        dcSignature = self.dcSign(plaintext)
        secureData = self.dcEncript(dcSignature)
        return secureData

    def dcEncript(self, dcSignature):
        remainder = len(dcSignature) % 16
        amountPadding = 16 - remainder
        encryptor = AES.new(self.keyAES, AES.MODE_CBC, self.iv)
        if(amountPadding == 0):
            data = (" " * 15)+","+dcSignature
        else:
            data = (" " * (amountPadding - 1))+","+dcSignature
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

    def dcSign(self, plaintext):
        hashVal = hashlib.sha256(plaintext).digest()
        (rsaSignature, ) = self.rsaKeyObj.sign(hashVal, '')
        rsaSignature = str(rsaSignature)
        dcSignature = str(len(plaintext))+ ","+ plaintext + rsaSignature
        return dcSignature

    def dcVerify(self, dcSignature):
        l = ""
        i = 0
        # for i in range(0, len(dcSignature)):
        #     c = dcSignature[i]
        #     if c == ",":
        #         break
        #     l += c
        while i < len(dcSignature):
            c = dcSignature[i]
            if c == ",":
                break
            l += c
            i += 1
        index_signature = i + 1 + int(l)
        plaintext = dcSignature[i+1:index_signature]
        rsaSignature = dcSignature[index_signature:]
        signature_to_verify = (long(rsaSignature), ) #tuple for rsa pycrypto should have (rsa_signature, )
        hash_val = hashlib.sha256(plaintext).digest()
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
        saltIv = hashlib.sha256(str(pathToKeyFilename)).digest()
        self.iv = makeIV(self.keyAES, saltIv)
        self.rsaKeyObj = makeRSAKeyObj(password, salt)

    def __eq__(self, otherKey):
        if not isinstance(otherKey, DCTableKey):
            return False
        boolean = (otherKey.keyAES == self.keyAES)
        boolean = boolean and (self.iv == otherKey.iv)
        boolean = boolean and equalRSAKeys(self.rsaKeyObj, otherKey.rsaKeyObj)
        return boolean

    def __ne__(self, otherKey):
        return not self.__eq__(otherKey)


class DCFileKey(DCKey):
    def __init__(self, iv, keyAES, rsaRandNum):
        self.keyAES = keyAES
        self.iv = iv
        self.rsaRandNum = rsaRandNum
        salt = hashlib.sha256(iv).digest()
        self.rsaKeyObj = makeRSAKeyObj(rsaRandNum, salt)

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

    def __eq__(self, otherKey):
        if not isinstance(otherKey, DCFileKey):
            return False
        boolean = (otherKey.keyAES == self.keyAES)
        # print "AES Key: ", (otherKey.keyAES,self.keyAES)
        # print "AES: ", boolean
        boolean = boolean and (self.iv == otherKey.iv)
        #print "iv: ", boolean
        boolean = boolean and equalRSAKeys(self.rsaKeyObj, otherKey.rsaKeyObj)
        #print "rsaKeyObj equality: ", boolean
        return boolean

    def __ne__(self, otherKey):
        return not self.__eq__(otherKey)




class DCCryptoClient:
    def __init__(self):
        #maps name of file to its key object
        self.pathsToKeys = {}

    def addKeyObj(self, pathname, keyObj):
        #adds a key=name maping to value=keyObj to the dictionary
        self.pathsToKeys[pathname] = keyObj

    def getKey(self, pathname):
        return self.htKeys.get(pathname)

    def encryptName(self, name, keyObj):
        return keyObj.dcEncrypt(name) 

    def dencryptName(self, encryptname, keyObj):
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
        for i in range(0,len(keyFileData)):
            c = keyFileData[i]
            if (c != ","):
                currentKeyLength+=c
            else:
                keysLengths.append(currentKeyLength)
                currentKeyLength = ""
                commas += 1
                if(commas == 3):
                    break
        ivLen = int(keysLengths[0])
        keyAESLen = int(keysLengths[1])
        rsaKeyObjLen = int(keysLengths[2])
        startKeyAES = i+1+ivLen
        startRSAnum = startKeyAES+keyAESLen

        iv = keyFileData[i+1:startKeyAES]
        keyAES = keyFileData[startKeyAES:startRSAnum]
        rsaRandNum = keyFileData[startRSAnum:]
        keyFileObj = DCFileKey(iv, keyAES, rsaRandNum)
        return keyFileObj


def encryptAES(keyAES, iv, plaintext, mode = AES.MODE_CBC):
    encryptor = AES.new(keyAES, mode, iv)
    ciphertext = encryptor.encrypt(plaintext)
    return ciphertext

def makeKeyAES(password, salt = os.urandom(32)):
    keyAES = pbkdf2.PBKDF2(str(password), str(salt)).read(32)
    return keyAES

def makeIV(key, salt = os.urandom(32)):
    iv = pbkdf2.PBKDF2(str(key), salt).read(16)
    return iv

def equalRSAKeys(rsaKey1, rsaKey2):
    public_key = rsaKey1.publickey().exportKey("DER") 
    private_key = rsaKey1.exportKey("DER") 
    pub_new_key = rsaKey2.publickey().exportKey("DER")
    pri_new_key = rsaKey2.exportKey("DER")
    boolprivate = (private_key == pri_new_key)
    #print "boolpri", boolprivate
    boolpublic = (public_key == pub_new_key)
    #print "boolpub", boolpublic
    return (boolprivate and boolpublic)

def makeRSAKeyObj(password, salt):
    #careful with changing this function.
    #if you don't know how it works, changing it might break the library completely.
    master_key = PBKDF2(password, salt, count=10000)  # bigger count = better
    def my_rand(n):
        # PBKDF2 with count=1 and a variable salt makes a handy key-expander
        my_rand.counter += 1
        #return PBKDF2(master_key, salt, dkLen=n, count=1)
        return PBKDF2(master_key, "my_rand:%d" % my_rand.counter, dkLen=n, count=1)
    my_rand.counter = 0
    RSA_key = RSA.generate(2048, randfunc=my_rand)
    return RSA_key

#keyFileData = DCCryptoClient().makeKeyFile("orochimaru" , "kitty")
#print keyFileData
# tableKey = DCTableKey('password', 'username', 'keyFilename')
# plaintext = "brando"
# secureData = tableKey.lock(plaintext)
# decryptedData = tableKey.unlock(secureData)


