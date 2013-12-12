#!/usr/bin/env python

import httplib
import sys
import DCCryptoClient
import os

def keychainFn(self, name, username):
    return '.kc-' + username + '-' + name

def lsFn(dirname):
    return '.ls-' + dirname

def createAccount(username, passwd):
    HttpClient = DCHTTPClient('127.0.0.1', 8080)
    dn = username
    kcFn = keychainFn(dn, username)
    lsFn = lsFn(dn)

    userKeychain = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, kcFn)

    dirKeychain = DCCryptoClient.createKeyFileObj()
    encryptedDirKeychainFn = DCCryptoClient.encryptName(kcFn, userKeychain) #is this the right key
    encryptedDn = DCCryptoClient.encryptName(dn, dirKeychain)
    encrypted_lsFn = DCCryptoClient.encryptName(lsFn, dirKeychain)

    secureKeyContent = keyObj.toSecureString(self.username, self.passwd, encryptedKeyName)

    #keyfile
    self.HttpClient.sendCreateRequest(encryptedDirKeychainFn,
                                    True,
                                    False,
                                    secureKeyContent)

    #lsfile
    secureFileContent = DCCryptoClient.encryptFile("", keyObj)
    self.HttpClient.sendCreateRequest(encrypted_lsFn,
                                    True,
                                    False,
                                    secureFileContent)

    #directory
    self.HttpClient.sendCreateRequest(encryptedDn,
                                    False,
                                    True)
    
    return DCClient(username, passwd)

class DCClient:
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd
        self.wd = DCWorkingDirectory(self.username, self.passwd)
        self.HttpClient = DCHTTPClient('127.0.0.1', 8080)

    def createFile(self, fn, content):
        kcFn = keychainFn(fn, self.username)
        path = self.wd.pwd()
        userKeychain = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)

        fileKeychain = DCCryptoClient.createKeyFileObj()
        encryptedFileKeychainFn = DCCryptoClient.encryptName(path + '/' + kcFn, userKeychain) #is this the right key
        encryptedFn = DCCryptoClient.encryptName(path + '/' + fn, fileKeychain)

        parentDn = self.wd.up(1)
        parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.password, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
        # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
        dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
        # plaintextFn, encryptedFn, plaintextFileKeychainFn, encryptedFileKeychainFn, httpClient
        dcdir.registerFile(encryptedFn, fn, encryptedFileKeychainFn, kcFn, self.HttpClient)
        self.wd.down(parentDn)

        # # *** BEGIN: Replaced with DCDir implementation above ***

        #     #request to read parent directory contents to add new files
        #     parentName = self.wd.up(1) # returns name of directory after the last slash
        #     #need to use lsfile here instead
        #     dirObj = readSecureDirObj(parentName)
        #     dirObj.add(encryptedKeyName, kfname)
        #     dirObj.add(encryptedName, name)
        #     dirObj.sort()

        #     #request to write the modified directory
        #     self.write(parentName, dirObj.content(), True)

        #     self.wd.down(parentName)

        # # --- END ---


        #request to create key file on server        
        encryptedPath = self.wd.encrypted_pwd() 
        secureKeyContent = fileKeychain.toSecureString(self.username, self.passwd, encryptedPath + '/' + encryptedFileKeychainFn)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedFileKeychainFn,
                                        True,
                                        False,
                                        secureKeyContent)

        #request to create regular file on server

        #need to encrypt empty string?
        secureFileContent = DCCryptoClient.encryptFile(content, fileKeychain)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedFn,
                                        True,
                                        False,
                                        secureFileContent)

        return "Created file: ", name

    def mkdir(self, name):
        dn = name
        kcFn = keychainFn(dn, self.username)
        lsFn = lsFn(dn)
        path = self.wd.toString()

        userKeychain = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)

        dirKeychain = DCCryptoClient.createKeyFileObj()
        encryptedDirKeychainFn = DCCryptoClient.encryptName(path + '/' + kcFn, userKeychain) #is this the right key
        encryptedDn = DCCryptoClient.encryptName(path + '/' + dn, dirKeychain)
        encrypted_lsFn = DCCryptoClient.encryptName(path + '/' + lsFn, dirKeychain) # is the path needed??

        parentDn = self.wd.up(1)
        parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.password, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
        # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
        dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
        # plaintextDn, encryptedDn, plaintext_lsFn, encrypted_lsFn, plaintextFileKeychainFn, encryptedFileKeychainFn, httpClient
        dcdir.registerDir(encryptedDn, dn, encrypted_lsFn, lsFn, encryptedDirKeychainFn, kcFn, self.HttpClient)
        self.wd.down(parentDn)

        # # *** BEGIN: Replaced with DCDir implementation above ***
        # #request to read parent directory contents to add new directory
        #     parentName = self.wd.up(1) # returns name of directory after the last slash
        #     dirObj = readSecureDirObj(parentName)
        #     dirObj.add(encryptedKeyName, kfname)
        #     dirObj.add(encryptedName, name)
        #     dirObj.add(encryptedLSFileName, lsname)
        #     dirObj.sort()

        #     #request to write the modified directory
        #     self.write(parentName, dirObj.content(), True)

        #     self.wd.down(parentName)
        # # --- 

        #request to create key file and directory on server
        
        encryptedPath = self.wd.encrypted_pwd()
        secureKeyContent = dirKeychain.toSecureString(self.username, self.passwd, encryptedPath + '/' + encryptedDirKeychainFn)

        #keyfile
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedDirKeychainFn,
                                        True,
                                        False,
                                        secureKeyContent)

        #lsfile
        secureFileContent = DCCryptoClient.encryptFile("", dirKeychain)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encrypted_lsFn,
                                        True,
                                        False,
                                        secureFileContent)

        #directory
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedDn,
                                        False,
                                        True)

        return "Created directory: ", name

    def read(encryptedName):
        encryptedPath = self.wd.encrypted_pwd()
        content = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeyFileName)
        return content

    def readFile(name):
        kfname = tableFilename(name)
        path = self.wd.toString()
        mkObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)

        #get encrypted keyfile name
        encryptedKeyFileName = DCCryptoClient.encryptedName(path + '/' + kfname, mkObj)

        #TODO:check that keys exist for all parts of the encrypted path

        secureKeyfileContent = self.read(encryptKeyFileName)

        #construct key object
        keyObj = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, path + '/' + kfname)

        #save keyobj for later
        DCCryptoClient.addKeyObj(path + '/' + kfname, keyObj)

        #request encrypted file using encrypted file name
        encryptedFileName = DCCryptoClient.encryptName(path + '/' + name, keyObj)

        encryptedFileContent = self.read(encryptedFileName)

        #decrypt file contents
        decryptedFileContent = DCCryptoClient.decryptFile(encryptedFileContent, keyObj)

        #verify contents

        return decryptedFileContent

    # def readSecureDirObj(name):
    #     kfname = tableFilename(name)
    #     lsname = lsFilename(name)
    #     path = self.wd.toString()
    #     mkObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)

    #     #get encrypted keyfile name
    #     encryptedKeyFileName = DCCryptoClient.encryptName(path + '/' + kfname, mkObj)

    #     #TODO:check that keys exist for all parts of the encrypted path

    #     encryptedPath = self.wd.encrypted_pwd()

    #     #request keyfile
    #     secureKeyfileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeyFileName)

    #     #construct key object
    #     keyObj = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd)

    #     #save keyobj for later
    #     DCCryptoClient.addKeyObj(path + '/' + lsname, keyObj)

    #     #request encrypted file using encrypted file name
    #     encryptedLSFileName = DCCryptoClient.encryptName(path + '/' + lsname, keyObj)
    #     encryptedDirName = DCCryptoClient.encryptName(path + '/' + name, keyObj)

    #     encryptedLSFileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedLSFileName)
    #     dirContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedDirName)

    #     #decrypt file contents
    #     decryptedLSFileContent = DCCryptoClient.decryptFile(encryptedLSFileContent, keyObj)

    #     #verify contents
    #     dirObj = DCSecureDir(dirContent, decryptedLSFileContent)

    #     return dirObj
    
    def readDir(name):
        dirObj = self.readSecureDirObj(name)
        return dirObj.getLS()

    def write(name, content, isLS=False):
        kfname = tableFilename(name)
        if isLS:
            name = lsFilename(name)
        path = self.wd.toString()
        mkObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)

        #TODO: If file doesn't exist create it

        #get associated key for this file
        if DCCryptoClient.hasKey(kfname):
            keyObj = DCCryptoClient.getKey(kfname)
        else:
            #request keyfile
            encryptedKeyFileName = DCCryptoClient.encryptName(path + '/' + kfname, mkObj)
            encryptedPath = self.wd.encrypted_pwd()
            secureKeyfileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeyFileName)
            keyObj = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, path + '/' + kfname)

        #encrypt file's new contents
        encryptedContent = DCCryptoClient.encryptFile(content, keyObj)

        #craft write request to server
        encryptedFileName = DCCryptoClient.encryptName(path + '/' + name, keyObj)
        encryptedPath = self.wd.encrypted_pwd()

        self.HttpClient.sendWriteRequest(encryptedPath + '/' + encryptedFileName,
                                         encryptedContent)

        return name + " written"

    def deleteFile(fn):
        kcFn = keychainFn(fn, self.username)
        path = self.wd.pwd()
        userKeychain = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)


        #------- request to delete key file ----------
        #get encrypted keyfile name
        encryptedFileKeychainFn = DCCryptoClient.encryptName(path + '/' + kcFn, userKeychain)

        #request keyfile
        secureKeychainContent = self.HttpClient.sendReadRequest(self.wd.encrypted_pwd() + '/' + encryptedFileKeychainFn)

        #construct key object
        dirKeychain = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeychainContent, self.username, self.passwd)

        #request encrypted file using encrypted file name
        encryptedDn = DCCryptoClient.encryptName(path + '/' + dn, dirKeychain)

        parentDn = self.wd.up(1)
        parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.password, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
        # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
        dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
        # 
        dcdir.unregisterDir(encryptedFn, encryptedFileKeychainFn, self.HttpClient)
        self.wd.down(parentDn)

        # # *** BEGIN: Replaced with DCDir implementation above ***
        #     # -- request to change parent directory structure --
        #     #request to read parent directory contents to add new directory
        #     parentName = self.wd.up(1) # returns name of directory after the last slash
        #     dirObj = readSecureDirObj(parentName)
        #     dirObj.remove(encryptedKeyName, kfname)
        #     dirObj.remove(encryptedName, name)
        #     dirObj.sort()

        #     #request to write the modified directory
        #     self.write(parentName, dirObj.content(), True)

        #     self.wd.down(parentName)
        # # --- END ---

        #---------- request to delete file -----------
        #delete keyfile
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedKeyName)

        #delete file
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedFileName)

        return

    # rmdir => dirs only
    def rmdir(args):
        dn = args[0]
        kcFn = keychainFn(dn, self.username)
        lsFn = lsFn(name)
        path = self.wd.toString()
        userKeychain = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)

        #------- request to delete key directory ----------
        #get encrypted keyfile name
        encryptedKeyFn = DCCryptoClient.encryptName(path + '/' + kcFn, userKeychain)
        encryptedPath = self.wd.encrypted_pwd()

        #request keyfile
        secureKeyfileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeyFn)

        #construct key object
        dirKeychain = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd)

        #request encrypted file using encrypted file name
        encryptedDn = DCCryptoClient.encryptName(path + '/' + dn, dirKeychain)
        encrypted_lsFn = DCCryptoClient.encryptName(path + '/' + lsFn, dirKeychain)

        parentDn = self.wd.up(1)
        parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.password, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
        # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
        dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
        # plaintextDn, encryptedDn, plaintext_lsFn, encrypted_lsFn, plaintextDirKeychainFn, encryptedDirKeychainFn, httpClient
        dcdir.unregisterDir(encryptedDn, encrypted_lsFn, encryptedDirKeychainFn, self.HttpClient)
        self.wd.down(parentDn)

        # # *** BEGIN: Replaced with DCDir implementation above ***

        # # -- request to change parent directory structure --
        # #request to read parent directory contents to add new directory
        # parentName = self.wd.up(1) # returns name of directory after the last slash
        # dirObj = readSecureDirObj(parentName)
        # dirObj.remove(encryptedKeyName, kfname)
        # dirObj.remove(encryptedName, name)
        # dirObj.remove(encryptedLSFileName, lsname)
        # dirObj.sort()

        # #request to write the modified directory
        # self.write(parentName, dirObj.content(), True)

        # self.wd.down(parentName)

        # # --- END ---

        #---------- request to delete directory -----------
        #delete keyfile
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedKeyName)

        #delete file
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedFileName)

        #delete ls file
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedLSFileName)

        return

    def rename(args, isDir=False):
        name = args[0]
        newName = args[1]
        kcFn = keychainFn(name, self.username)
        newKcFn = keychainFn(newName, self.username)
        lsFn = lsFilename(name)
        new_lsFn = lsFilename(lsname)
        path = self.wd.pwd()
        userKeychain = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)
        newUserKeychain = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + newKcFn)

        #TODO: check if name exists?
        #TODO: update keys in Key dictionary

        #------- get new encrypted names ----------
        #get encrypted keyfile name
        encryptedKeychainFn = DCCryptoClient.encryptName(path + '/' + kcFn, userKeychain)
        newEncryptedKeychainFn = DCCryptoClient.encryptName(path + '/' + newKcFn, newUserKeychain)
        encryptedPath = self.wd.encrypted_pwd()

        #request keyfile
        secureKeychainContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeychainFn)

        #construct key object
        keyChain = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeychainContent, self.username, self.passwd)

        #request encrypted file using encrypted file name
        encryptedName = DCCryptoClient.encryptName(path + '/' + name, keyChain)
        newEncryptedName = DCCryptoClient.encryptName(path + '/' + newName, keyChain)
        encrypted_lsFn = None
        newEncrypted_lsFn = None
        if isDir:
            encrypted_lsFn = DCCryptoClient.encryptName(path + '/' + lsFn, keyChain)
            newEncrypted_lsFn = DCCryptoClient.encryptName(path + '/' + new_lsFn, keyChain)

        parentDn = self.wd.up(1)
        parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.password, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
        # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
        dcdir = DCDir(parentDn, self.wd.pwd(), parentDirEncryptedPath, parentDirKeychain)
        
        if isDir: # renaming a dir
            # Unregisted encryptedDn, encryptedKeychainFn, encrypted_lsFn
            dcdir.unregisterDir(encryptedName, encryptedPath, self.HttpClient)
            # Register newEncryptedDn, newPlaintextDn, newEncryptedKeychainFn, newPlaintextKeychainFn, newEncrypted_lsFn, new_lsFn httpClient
            dcdir.registerDir(newEncryptedName, newName, newEncryptedKeychainFn, newKcFn, newEncrypted_lsFn, new_lsFn, self.HttpClient)
        else: # renaming a file
            # Unregisted encryptedName, encryptedKeychainFn
            dcdir.unregisterFile(encryptedName, encryptedKeychainFn, self.HttpClient)
            # Register newEncryptedFn, newPlaintextFn, newEncryptedKeychainFn, newPlaintextKeychainFn, httpClient
            dcdir.registerFile(newEncryptedName, newName, newEncryptedKeychainFn, newKcFn, self.HttpClient)
        self.wd.down(parentDn)


        # # *** BEGIN Replaced with DCDir implementation above ***

        #     # -- request to change parent directory structure --
        #     #request to read parent directory contents to add new directory
        #     parentName = self.wd.up(1) # returns name of directory after the last slash
        #     dirObj = readSecureDirObj(parentName)
        #     dirObj.remove(encryptedKeyName, kfname)
        #     dirObj.remove(encryptedName, name)
        #     dirObj.add(newEncryptedFileName, newName)
        #     dirObj.add(newEncryptedKeyName, newKFName)
        #     if isDir:
        #         dirObj.remove(encryptedLSFileName, lsname)
        #         dirObj.add(newEncryptedLSFileName, newLSName)
        #     dirObj.sort()

        #     #request to write the modified directory
        #     self.write(parentName, dirObj.content(), True)

        #     self.wd.down(parentName)

        # # --- END ---

        # -------- set new names -------------------
        self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedFileName,
                                        encryptedPath + '/' + newEncryptedFileName)
        self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeyName,
                                        encryptedPath + '/' + newEncryptedKeyName)
        if isDir:
            self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedLSFileName,
                                            encryptedPath + '/' + newEncryptedLSFileName)

# -------------------------------


# *** Working Directory Class ***

class DCWorkingDirectory:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.currentRoot = username
        self.pwd = []

    def root():
        return '/' + self.currentRoot + '/'

    def switchRoot(otherUser):
        self.currentRoot = otherUser
        self.pwd = []

    def restoreRoot():
        switchRoot(username)

    def up(steps=1):
        newWD = None
        for i in xrange(0, steps):
            if len(self.pwd) > 0:
                newWD = self.pwd.pop()
            else:
                return newWD

    def down(subdirectory):
        self.pwd.append(subdirectory)

    def path(directories):
        return self.root() + '/'.join(directories)

    def pwd():
        return self.path(self.pwd)

    def encrypted_pwd():
        encrypted_pwd = []
        for i in range(0,len(self.pwd)):
            dirname = self.pwd[0]
            path = self.path(self.pwd[:i])
            # see if we can get the encrypted name without querying the server
            dirKey = dcCryptoClient.getKey(path)
            if not dirKey:
               raise ValueError("cd'ing through multiple directories at once is not yet implemented. Must manually cd through them.")

            # encrypt dirname with key            
            encryptedDirname = dcCryptoClient.encryptName(dirname, dirKey)
            encrypted_pwd.append(encryptedDirname)
        return self.path(encrypted_pwd)

# -----------------------------------


# *** Dark Cloud Secure Directory ***

class DCDir:

    # *** Class attrs & methods ***

    @staticmethod
    def lsFn(dirname):
        return '.ls-' + dirname

    @staticmethod
    def addFile_lsEntry(lsFile, plaintextFn, encryptedFn):
        # Entry looks as follows: 
        #   entryLength,fn/dn,ptNameLength,encNameLength,ptName,encName;
        ptFnLength = len(plaintextFn)
        encFnLength = len(encryptedFn)
        lengthlessEntry = 'fn,' + str(ptFnLength) + ',' + str(encFnLength) + ',' + plaintextFn + ',' + encryptedFn + ';'
        entryLength = len(lengthlessEntry) + 1 # comma (below) takes one character
        entry = str(entryLength) + ',' + lengthlessEntry
        return lsFile + entry

    @staticmethod
    def removeFile_lsEntry(lsFile, encryptedFn):
        offset = 0
        updated_lsFile = None
        while offset < len(lsFile):
            entry, newOffset = DCDir.readEntry(lsFile, offset)
            if entry.isFile and (entry.encryptedName == encryptedFn):
                #remove entry
                updated_lsFile = lsFile[:offset] + lsFile[newOffset:]
            offset = newOffset
        return updated_lsFile

        

    @staticmethod
    def addDir_lsEntry(lsFile, plaintextDn, encryptedDn):
        # Entry looks as follows: 
        #   entryLength,fn/dn,ptNameLength,encNameLength,ptName,encName;
        ptDnLength = len(plaintextDn)
        encDnLength = len(encryptedDn)
        lengthLessentry = 'dn,' + str(ptDnLength) + ',' + str(encDnLength) + ',' + plaintextDn + ',' + encryptedDn + ';'
        entryLength = len(lengthlessEntry) + 1 # comma (below) takes one character
        entry = entryLength + ',' + lengthlessEntry
        return lsFile + entry
        

    @staticmethod
    def removeDir_lsEntry(lsFile, encryptedDn):
        offset = 0
        updated_lsFile = None
        while offset < len(lsFile):
            entry, newOffset = DCDir.readEntry(lsFile, offset)
            if entry.isDir and (entry.encryptedName == encryptedFn):
                #remove entry
                updated_lsFile = lsFile[:offset] + lsFile[newOffset:]
            offset = newOffset
        return updated_lsFile

    @staticmethod
    # Assume index starts at correct offset
    def readEntry(lsFile, offset):
        # returns: (entryObj, nextOffset)
        # Entry looks as follows: 
        #   entryLength,fn/dn,ptNameLength,encNameLength,ptName,encName;
        # lengths:: entry length, ptName length, and encName length
        lengths = []
        isFile = False
        isDir = False
        commaCount = 0
        stringBuilder = ''
        plaintextNameStart = None
        for i in range(offset,len(lsFile)):
            char = lsFile[i]
            if char != ',':
                stringBuilder += char
            else:
                commaCount +=1
                if commaCount == 2: # currently building fn/dn
                    if stringBuilder == 'fn':
                        isFile = True
                    elif stringBuilder == 'dn':
                        isDir = True
                else: # currenty building a length
                    length = int(stringBuilder)
                    lengths.append(length)
                    if commaCount == 4:
                        plaintextNameStart = i + 1
                        break
                # Reset stringBuilder
                stringBuilder = ''
        entryLength = lengths[0]
        plaintextNameLength = lengths[1]
        encryptedNameLength = lengths[2]
        plaintextName = lsFile[plaintextNameStart:plaintextNameStart+plaintextNameLength]
        encryptedNameStart = plaintextNameStart + plaintextNameLength + 1
        encryptedName = lsFile[encryptedNameStart:encryptedNameStart+encryptedNameLength]
        trueEntryLength = entryLength + len(str(entryLength))
        return (DClsEntry(isFile, isDir, plaintextName, encryptedName), offset + trueEntryLength)


    @staticmethod
    def verifiedDirKeychain(username, password, dn, encryptedDirpath, httpClient):
        userKeychain = dcCryptoClient.createUserMasterKeyObj(username, password, encrypted_pwd)
        # Get encrypted dirKeychainFn name
        encryptedDirKeychainFn = dcCryptoClient.encryptName(keychainFn(dn, username), userKeychain)
        # Query server for secure dirKeychain
        secureDirKeychain = httpClient.sendReadRequest(encrypted_pwd)
        # Unlock dirKeychain and return it
        # secureKeyFileData, username, password, keyFileName
        return dcCryptoClient.makeKeyFileObjFromSecureKeyData(secureDirKeychain, username, password, encrypted_pwd)

    @staticmethod
    def sorted_lsEntries(lsFile):
        entries = []
        offset = 0
        while offset < len(lsFile):
            entry, newOffset = DCDir.readEntry(lsFile, offset)
            entries.append(entry)
            offset = newOffset
        # Sort by encrypted entry names
        sorted_entries = sorted(entries, key=lambda entry: entry.encrytedName)
        # Sorted lsFile construction
        return ''.join([str(sorted_entry) for sorted_entry in sorted_entries])

    @staticmethod
    def verifyWith_lsFile(encryptedDirEntries, lsFile):
        # If successful, returns a list of plaintext names of directory entries
        # encryptedDirEntries should be the array received from the server 
        #   i.e. (result of a read directory request)
        # Sort encrypted dir contents
        sortedEncryptedDirEntries = sorted(encryptedDirEntries, key=lambda dirEntry: dirEntry)
        offset = 0
        entryCounter = 0
        plaintextEntryNames = []
        while offset < len(lsFile):
            encryptedNameFromDir = sortedEncryptedDirEntries[entryCounter]
            lsFileEntry, newOffset = DCDir.readEntry(lsFile, offset)
            if (encryptedNameFromDir != lsFileEntry.encryptedName):
                # Mismatch in sorted entries
                raise ValueError("DCDir verification failed!")
            plaintextEntryNames.append(lsFileEntry.plaintextName)
            offset = newOffset
            entryCounter += 1
        # Different number of entries
        if (entryCounter != len(sortedEncryptedDirEntries)):
            raise ValueError("DCDir verification failed!")
        return plaintextEntryNames

    # ------------------------


    # *** Instance methods ***

    def __init__(self, dn, encryptedDirpath, dirKeychain): # how should this be initialized
        self.dn = dn
        self.encryptedDirname = DCCryptoClient.encryptName(dn, dirKeychain)
        self.encryptedDirpath = encryptedDirpath
        self.lsFn = DCDir.lsFn(dn)
        self.encrypted_lsFn = dcCryptoClient.encryptName(self.lsFn, dirKeychain)
        self.dirKeychain = dirKeychain
    
    def fullEncryptedPath(name):
        return self.encryptedDirpath + '/' + name

    # Add file to directory ls file
    def registerFile(encryptedFn, plaintextFn, encryptedFileKeychainFn, plaintextFileKeychainFn, httpClient):
        # - Query server for secure ls file
        secure_lsFile = httpClient.sendReadRequest(self.fullEncryptedPath(self.encrypted_lsFn))
        # - Unlock (decrypt/verify) ls file
        lsFile = self.dirKeychain.unlock(secure_lsFile)
        # - Update ls file with new filename and fileKeychain filename (plaintext & encrypted name)
        lsFile_file = DCDir.addFile_lsEntry(lsFile, plaintextFn, encryptedFn)
        lsFile_file_keychain = DCDir.addFile_lsEntry(lsFile_file, plaintextFileKeychainFn, encryptedFileKeychainFn)
        # -Sort updated ls file
        updatedSorted_lsFile = DCDir.sorted_lsEntries(lsFile_file_keychain)
        # - Secure (sign/encrypt) updated, sorted ls file
        updatedSecure_lsFile = self.dirKeychain.lock(updatedSorted_lsFile)
        # - Query server to overwrite secure ls file
        return httpClient.sendWriteRequest(self.fullEncryptedPath(self.encrypted_lsFn), updatedSecure_lsFile)

    # Remove file from directory ls file
    def unregisterFile(encryptedFn, encryptedFileKeychainFn, httpClient):
        # - Query server for secure ls file
        secure_lsFile = httpClient.sendReadRequest(self.fullEncryptedPath(self.encrypted_lsFn))
        # - Unlock (decrypt/verify) ls file
        lsFile = self.dirKeychain.unlock(secure_lsFile)
        # - Update ls file by removing filename and fileKeychain name (plaintext & encrypted name)
        lsFile_file = DCDir.removeFile_lsEntry(lsFile, encryptedFn)
        lsFile_file_keychain = DCDir.removeFile_lsEntry(lsFile_file, encryptedFileKeychainFn)
        # - Sort updated ls file
        updatedSorted_lsFile = DCDir.sorted_lsEntries(lsFile_file_keychain)
        # - Secure (sign/encrypt) updated, sorted ls file
        updatedSecure_lsFile = self.dirKeychain.lock(updatedSorted_lsFile)
        # - Query server to overwrite secure ls file
        return httpClient.sendWriteRequest(self.fullEncryptedPath(self.encrypted_lsFn), updatedSecure_lsFile)

    # Add dir to directory ls file
    def registerDir(encryptedDn, plaintextDn, encrypted_lsFn, plaintext_lsFn, encryptedDirKeychainFn, plaintextDirKeychainFn, httpClient):
        # - Query server for secure ls file
        secure_lsFile = httpClient.sendReadRequest(self.fullEncryptedPath(self.encrypted_lsFn))
        # - Unlock (decrypt/verify) ls file
        lsFile = self.dirKeychain.unlock(secure_lsFile)
        # - Update ls file with new filename and fileKeychain filename (plaintext & encrypted name)
        lsFile_dir = DCDir.addDir_lsEntry(lsFile, plaintextDn, encryptedDn)
        lsFile_dir_ls = DCDir.addFile_lsEntry(lsFile_dir, plaintext_lsFn, encrypted_lsFn)
        lsFile_dir_ls_keychain = DCDir.addFile_lsEntry(lsFile_dir_ls, plaintextDirKeychainFn, encryptedDirKeychainFn)
        # - Sort updated ls file
        updatedSorted_lsFile = DCDir.sorted_lsEntries(lsFile_dir_ls_keychain)
        # - Secure (sign/encrypt) updated, sorted ls file
        updatedSecure_lsFile = self.dirKeychain.lock(updatedSorted_lsFile)
        # - Query server to overwrite secure ls file
        return httpClient.sendWriteRequest(self.fullEncryptedPath(self.encrypted_lsFn), updatedSecure_lsFile)

    # Remove dir from directory ls file
    def unregisterDir(encryptedDn, encrypted_lsFn, encryptedDirKeychainFn, httpClient):
        # - Query server for secure ls file
        secure_lsFile = httpClient.sendReadRequest(self.fullEncryptedPath(self.encrypted_lsFn))
        # - Unlock (decrypt/verify) ls file
        lsFile = self.dirKeychain.unlock(secure_lsFile)
        # - Update ls file by removing dirname, dir_lsFile and dirKeychain filename (plaintext & encrypted name)
        lsFile_dir = DCDir.removeDir_lsEntry(lsFile, encryptedDn)
        lsFile_dir_ls = DCDir.removeFile_lsEntry(lsFile_dir, encrypted_lsFn)
        lsFile_dir_ls_keychain = DCDir.removeFile_lsEntry(lsFile_dir_ls, encryptedDirKeychainFn)
        # - Sort updated ls file
        updatedSorted_lsFile = DCDir.sorted_lsEntries(lsFile_dir_ls_keychain)
        # - Secure (sign/encrypt) updated, sorted ls file
        updatedSecure_lsFile = self.dirKeychain.lock(updatedSorted_lsFile)
        # - Query server to overwrite secure ls file
        return httpClient.sendWriteRequest(self.fullEncryptedPath(self.encrypted_lsFn), updatedSecure_lsFile)

# -------------------------------------


# *** Dark Cloud ls entry ***

class DClsEntry:
    def __init__(self, isFile, isDir, plaintextName, encryptedName):
        if (isFile and isDir) or (not isFile and not isDir):
            raise ValueError("Entry should be EITHER a filename OR a dirname")
        self.isFile = isFile
        self.isDir = isDir
        self.plaintextName = plaintextName
        self.encryptedName = encryptedName

    def __str__(self):
        fnSlashDn = ''
        if self.isFile:
            fnSlashDn = 'fn'
        elif self.isDir:
            fnSlashDn = 'dn'
        ptNameLength = len(self.plaintextName)
        encNameLength = len(self.encryptedName)
        lengthlessEntry = 'fn,' + str(ptNameLength) + ',' + str(encNameLength) + ',' + self.plaintextName + ',' + self.encryptedName + ';'
        entryLength = len(lengthlessEntry) + 1 # comma (below) takes one character
        entry = str(entryLength) + ',' + lengthlessEntry
        return entry


# -----------------------------


# *** Run Dark Cloud Client ***

def run():
    client = DarkCloudClient()
    try:
        while True:
            cmd_str = raw_input(prompt)
            args = shlex.split(cmd_str)
            if not args: continue
            cmd = args[0]
            client.run_command(cmd, args[1:])
    except EOFError:
        print "\nEnded Session"


if __name__ == '__main__':
    run()
