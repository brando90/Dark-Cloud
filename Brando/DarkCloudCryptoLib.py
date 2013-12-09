import os, random, struct, sys
import filecmp
from Crypto.Cipher import AES
import pbkdf2
import hashlib

class DCKey:
    def __init__(self):
        pass

    def unlock(self, contentToUnlock):
        pass

    def lock(self, contentToLock):
        pass

class DCTableKey(DCkey):
    __init__(self, password, username, keyFilename):
        #when making keys from password for a specific keyFilename
        salt = hashlib.sha256(username).digest()
        self.keyAES = makeKeyAES(password, salt)
        self.iv = makeIV(self.keyAES, keyFilename)
        self.rsaKeyObj = makeRSAKeyObj(password)

    def unlock(self, keyTableFileContent):

        return originalData

class DCFileKey(DCKey):
    __init__(self, ):
        





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

def encrypt_file(password, key_filename, file_name):
    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(file_name)

    with open(file_name, 'r') as f:
        file_data = f.read()
        delta = 0
        if len(file_data) % 16 != 0:
            delta = (16 - len(file_data)) % 16
            file_data += (' ' * delta)
        meta_data = str(filesize)+"\n"+str(iv)+"\n"+str(delta)
        return encryptor.encrypt(file_data)

def decrypt_file(key, file_name):
    with open(file_name, 'r') as f:
        origsize = struct.unpack('<Q', f.read(struct.calcsize('Q')))[0]
        iv = f.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        while True:
            file_data = f.read()
            outfile.write(decryptor.decrypt(chunk))

        outfile.truncate(origsize)


keyFileData = DCCryptoClient().makeKeyFile("orochimaru" , "kitty")
print keyFileData
