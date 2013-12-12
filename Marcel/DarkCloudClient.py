#!/usr/bin/env python

import httplib
import sys
from DCCryptoClient import *
import os
from DCHTTPClient import *

GDCCryptoClient = DCCryptoClient()
GDCHTTPClient = DCHTTPClient('127.0.0.1', 8080)

def keychainFn(name, username):
    print "kcFn start"
    print "kcFn name:" + name
    print "kcFn username" + username
    print "kcFn end"
    return '.kc-' + username + '-' + name

def nameTo_lsFn(dirname):
    return '.ls-' + dirname

def createAccount(username, passwd):
    print "createAccount"
    HttpClient = DCHTTPClient('127.0.0.1', 8080)
    dn = username
    kcFn = keychainFn(dn, username)
    lsFn = nameTo_lsFn(dn)
    cryptClient = DCCryptoClient()

    userKeychain = cryptClient.createUserMasterKeyObj(username, passwd, kcFn)

    dirKeychain = cryptClient.createKeyFileObj()
    encryptedDirKeychainFn = cryptClient.encryptName(kcFn, userKeychain) #is this the right key
    encryptedDn = cryptClient.encryptName(dn, dirKeychain)
    encrypted_lsFn = cryptClient.encryptName(lsFn, dirKeychain)

    secureKeyContent = dirKeychain.toSecureString(username, passwd, encryptedDirKeychainFn)

    #keyfile
    HttpClient.sendCreateRequest(encryptedDirKeychainFn,
                                    True,
                                    False,
                                    secureKeyContent)

    #lsfile

    secureFileContent = cryptClient.encryptFile("", dirKeychain)
    HttpClient.sendCreateRequest(encrypted_lsFn,
                                    True,
                                    False,
                                    secureFileContent)

    #directory
    HttpClient.sendCreateRequest(encryptedDn,
                                    False,
                                    True)
    
    return DCClient(username, passwd)

class DCClient:
    def __init__(self, username, passwd):
        print "DCClient username: " + repr(username)
        self.username = username
        self.passwd = passwd
        self.wd = DCWorkingDirectory(self.username, self.passwd)
        self.HttpClient = DCHTTPClient('127.0.0.1', 8080)
        self.cryptClient = DCCryptoClient()

    def createFile(self, fn, content):
        print "createFile"
        kcFn = keychainFn(fn, self.username)
        path = self.wd.pwd()
        userKeychain = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)

        fileKeychain = self.cryptClient.createKeyFileObj()
        encryptedFileKeychainFn = self.cryptClient.encryptName(path + '/' + kcFn, userKeychain) #is this the right key
        encryptedFn = self.cryptClient.encryptName(path + '/' + fn, fileKeychain)
        print ""
        parentDn = self.wd.up(1)
        print "looking for parent dir"
        if parentDn:
            print "self.username at createFile: " + self.username
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
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
        secureFileContent = self.cryptClient.encryptFile(content, fileKeychain)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedFn,
                                        True,
                                        False,
                                        secureFileContent)

        return "Created file: ", fn

    def mkdir(self, name):
        print "mkdir"
        dn = name
        kcFn = keychainFn(dn, self.username)
        lsFn = nameTo_lsFn(dn)
        path = self.wd.pwd()

        userKeychain = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)

        dirKeychain = self.cryptClient.createKeyFileObj()
        encryptedDirKeychainFn = self.cryptClient.encryptName(path + '/' + kcFn, userKeychain) #is this the right key
        encryptedDn = self.cryptClient.encryptName(path + '/' + dn, dirKeychain)
        encrypted_lsFn = self.cryptClient.encryptName(path + '/' + lsFn, dirKeychain) # is the path needed??

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
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
        secureFileContent = self.cryptClient.encryptFile("", dirKeychain)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encrypted_lsFn,
                                        True,
                                        False,
                                        secureFileContent)

        #directory
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedDn,
                                        False,
                                        True)

        return "Created directory: ", name

    def read(self, encryptedName):
        encryptedPath = self.wd.encrypted_pwd()
        content = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedName)
        return content

    def readFile(self,name):
        print "readFile"
        fn = name
        kcFn = keychainFn(fn, self.username)
        path = self.wd.pwd()
        
        userKeychain = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)

        #get encrypted keyfile name
        encryptedFileKeychainFn = self.cryptClient.encryptedName(path + '/' + kcFn, userKeychain)

        #TODO:check that keys exist for all parts of the encrypted path

        secureKeyfileContent = self.read(encryptedFileKeychainFn)

        #construct key object
        fileKeychain = self.cryptClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, path + '/' + kcFn)

        #save keyobj for later
        self.cryptClient.addKeyObj(path + '/' + kcFn, fileKeychain)

        #request encrypted file using encrypted file name
        encryptedFn = self.cryptClient.encryptName(path + '/' + fn, fileKeychain)

        encryptedFileContent = self.read(encryptedFn)

        #decrypt file contents
        decryptedFileContent = self.cryptClient.decryptFile(encryptedFileContent, fileKeychain)

        #verify contents

        return decryptedFileContent

    # def readSecureDirObj(name):
    #     kfname = tableFilename(name)
    #     lsname = lsFilename(name)
    #     path = self.wd.pwd()
    #     mkObj = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)

    #     #get encrypted keyfile name
    #     encryptedKeyFileName = self.cryptClient.encryptName(path + '/' + kfname, mkObj)

    #     #TODO:check that keys exist for all parts of the encrypted path

    #     encryptedPath = self.wd.encrypted_pwd()

    #     #request keyfile
    #     secureKeyfileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeyFileName)

    #     #construct key object
    #     keyObj = self.cryptClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd)

    #     #save keyobj for later
    #     self.cryptClient.addKeyObj(path + '/' + lsname, keyObj)

    #     #request encrypted file using encrypted file name
    #     encryptedLSFileName = self.cryptClient.encryptName(path + '/' + lsname, keyObj)
    #     encryptedDirName = self.cryptClient.encryptName(path + '/' + name, keyObj)

    #     encryptedLSFileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedLSFileName)
    #     dirContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedDirName)

    #     #decrypt file contents
    #     decryptedLSFileContent = self.cryptClient.decryptFile(encryptedLSFileContent, keyObj)

    #     #verify contents
    #     dirObj = DCSecureDir(dirContent, decryptedLSFileContent)

    #     return dirObj
    
    def readDir(self, name):
        print "readDir"
        dn = name
        kcFn = keychainFn(dn, self.username)
        lsFn = nameTo_lsFn(dn)
        path = self.wd.pwd()

        userKeychain = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)

        encryptedFileKeychainFn = self.cryptClient.encryptedName(path + '/' + kcFn, userKeychain)
        encryptedPath = self.wd.encrypted_pwd()

        #request keyfile
        secureKeyContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedFileKeychainFn)

        #construct key object
        dirKeychain = self.cryptClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd)

        #save keyobj for later
        self.cryptClient.addKeyObj(path + '/' + lsFn, dirKeychain)

        #request encrypted file using encrypted file name
        encrypted_lsFn = self.cryptClient.encryptName(path + '/' + lsFn, dirKeychain)
        encryptedDn = self.cryptClient.encryptName(path + '/' + dn, dirKeychain)

        encryptedLSFileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedLSFileName)
        encryptedDirEntries = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedDirName)

        #decrypt file contents
        lsFile = self.cryptClient.decryptFile(encryptedLSFileContent, keyObj)

        #verify contents
        plaintextEntryNames = DCDir.verifyWith_lsFile(encryptedDirEntries, lsFile)
        return plaintextEntryNames

    def ls(self):
        name = self.wd.up(1)
        entries = self.readDir(name)
        self.wd.down(name)
        return entries

    def write(self, name, content, isLS=False):
        print "write"
        fn = name
        kcFn = keychainFn(fn, self.username)
        if isLS:
            lsFn = nameTo_lsFn(dn)
        path = self.wd.pwd()
        
        userKeychain = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)

        #TODO: If file doesn't exist create it

        #get associated key for this file
        if self.cryptClient.hasKey(kcFn):
            fileKeychain = self.cryptClient.getKey(kcFn)
        else:
            #request keyfile
            encryptedKeychainFn = self.cryptClient.encryptName(path + '/' + kcFn, userKeychain)
            encryptedPath = self.wd.encrypted_pwd()
            secureKeyfileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeychainFn)
            fileKeychain = self.cryptClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, path + '/' + kcFn)

        #encrypt file's new contents
        encryptedContent = self.cryptClient.encryptFile(content, fileKeychain)

        #craft write request to server
        encryptedFn = self.cryptClient.encryptName(path + '/' + fn, fileKeychain)
        encryptedPath = self.wd.encrypted_pwd()

        self.HttpClient.sendWriteRequest(encryptedPath + '/' + encryptedFn,
                                         encryptedContent)

        return name + " written"

    def deleteFile(self, fn):
        print "deleteFile"
        kcFn = keychainFn(fn, self.username)
        path = self.wd.pwd()
        userKeychain = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)


        #------- request to delete key file ----------
        #get encrypted keyfile name
        encryptedFileKeychainFn = self.cryptClient.encryptName(path + '/' + kcFn, userKeychain)

        #request keyfile
        secureKeychainContent = self.HttpClient.sendReadRequest(self.wd.encrypted_pwd() + '/' + encryptedFileKeychainFn)

        #construct key object
        fileKeychain = self.cryptClient.makeKeyFileObjFromSecureKeyData(secureKeychainContent, self.username, self.passwd)

        #request encrypted file using encrypted file name
        encryptedFn = self.cryptClient.encryptName(path + '/' + fn, fileKeychain)

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            # 
            dcdir.unregisterFile(encryptedFn, encryptedFileKeychainFn, self.HttpClient)
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
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedFileKeychainFn)

        #delete file
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedFn)

        return

    # rmdir => dirs only
    def rmdir(self, args):
        print "rmdir"
        dn = args[0]
        kcFn = keychainFn(dn, self.username)
        lsFn = nameTo_lsFn(name)
        path = self.wd.pwd()
        userKeychain = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)

        #------- request to delete key directory ----------
        #get encrypted keyfile name
        encryptedKeychainFn = self.cryptClient.encryptName(path + '/' + kcFn, userKeychain)
        encryptedPath = self.wd.encrypted_pwd()

        #request keyfile
        secureKeyfileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeychainFn)

        #construct key object
        dirKeychain = self.cryptClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd)

        #request encrypted file using encrypted file name
        encryptedDn = self.cryptClient.encryptName(path + '/' + dn, dirKeychain)
        encrypted_lsFn = self.cryptClient.encryptName(path + '/' + lsFn, dirKeychain)

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
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
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedKeychainFn)

        #delete file
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedDn)

        #delete ls file
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encrypted_lsFn)

        return

    def rename(self, name, newName, isDir=False):
        print "rename"
        kcFn = keychainFn(name, self.username)
        newKcFn = keychainFn(newName, self.username)
        lsFn = lsFilename(name)
        new_lsFn = lsFilename(newName)
        path = self.wd.pwd()
        userKeychain = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kcFn)
        newUserKeychain = self.cryptClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + newKcFn)

        #TODO: check if name exists?
        #TODO: update keys in Key dictionary

        #------- get new encrypted names ----------
        #get encrypted keyfile name
        encryptedKeychainFn = self.cryptClient.encryptName(path + '/' + kcFn, userKeychain)
        newEncryptedKeychainFn = self.cryptClient.encryptName(path + '/' + newKcFn, newUserKeychain)
        encryptedPath = self.wd.encrypted_pwd()

        #request keyfile
        secureKeychainContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeychainFn)

        #construct key object
        keyChain = self.cryptClient.makeKeyFileObjFromSecureKeyData(secureKeychainContent, self.username, self.passwd)

        #request encrypted file using encrypted file name
        encryptedName = self.cryptClient.encryptName(path + '/' + name, keyChain)
        newEncryptedName = self.cryptClient.encryptName(path + '/' + newName, keyChain)
        encrypted_lsFn = None
        newEncrypted_lsFn = None
        if isDir:
            encrypted_lsFn = self.cryptClient.encryptName(path + '/' + lsFn, keyChain)
            newEncrypted_lsFn = self.cryptClient.encryptName(path + '/' + new_lsFn, keyChain)

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.encrypted_pwd(), self.HttpClient)
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
        self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedName,
                                        encryptedPath + '/' + newEncryptedName)
        self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeychainFn,
                                        encryptedPath + '/' + newEncryptedKeychainFn)
        if isDir:
            self.HttpClient.sendReadRequest(encryptedPath + '/' + encrypted_lsFn,
                                            encryptedPath + '/' + newEncrypted_lsFn)

# -------------------------------


# *** Working Directory Class ***

class DCWorkingDirectory:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.currentRoot = username
        self.directoryStack = []
        self.dcCryptoClient = DCCryptoClient()

    def root(self):
        kcFn = keychainFn(self.username, self.username)
        print "username: %s, password: %s" % (self.username, self.password)

        userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.password, kcFn)
        encryptedFileKeychainFn = GDCCryptoClient.encryptName(kcFn, userKeychain)
        print "trying to access eFKcFn: " + encryptedFileKeychainFn
        secureRootKeychain = GDCHTTPClient.sendReadRequest(encryptedFileKeychainFn)
        rootKeychain =  GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureRootKeychain, self.username, self.password, encryptedFileKeychainFn)
        encryptedRoot = GDCCryptoClient.encryptName(self.username,rootKeychain)
        print "Encrypted ROOT: " + encryptedRoot

        return encryptedRoot

    def switchRoot(self,otherUser):
        self.currentRoot = otherUser
        self.directoryStack = []

    def restoreRoot(self):
        self.switchRoot(username)

    def up(self,steps=1):
        newWD = None
        for i in xrange(0, steps):
            if len(self.directoryStack) > 0:
                newWD = self.directoryStack.pop()
            else:
                return newWD

    def down(self,subdirectory):
        self.directoryStack.append(subdirectory)

    def path(self,directories):
        return self.root() + '/'.join(directories)

    def pwd(self):
        return self.path(self.directoryStack)

    def encrypted_pwd(self):
        encrypted_pwd = []
        for i in range(0,len(self.directoryStack)):
            dirname = self.directoryStack[0]
            path = self.path(self.directoryStack[:i])
            # see if we can get the encrypted name without querying the server
            dirKey = self.dcCryptoClient.getKey(path)
            if not dirKey:
               raise ValueError("cd'ing through multiple directories at once is not yet implemented. Must manually cd through them.")

            # encrypt dirname with key            
            encryptedDirname = self.dcCryptoClient.encryptName(dirname, dirKey)
            encrypted_pwd.append(encryptedDirname)
        return self.path(encrypted_pwd)

# -----------------------------------


# *** Dark Cloud Secure Directory ***

class DCDir:

    # *** Class attrs & methods ***

    @staticmethod
    def nameTo_lsFn(dirname):
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
        print "verifiedDirKeychain"
        userKeychain = GDCCryptoClient.createUserMasterKeyObj(username, password, encryptedDirpath)
        # Get encrypted dirKeychainFn name
        encryptedDirKeychainFn = GDCCryptoClient.encryptName(keychainFn(dn, username), userKeychain)
        # Query server for secure dirKeychain
        secureDirKeychain = httpClient.sendReadRequest(encryptedDirpath)
        # Unlock dirKeychain and return it
        # secureKeyFileData, username, password, keyFileName
        return GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureDirKeychain, username, password, encryptedDirpath)

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
        self.cryptClient = DCCryptoClient()
        self.encryptedDirname = self.cryptClient.encryptName(dn, dirKeychain)
        self.encryptedDirpath = encryptedDirpath
        self.lsFn = DCDir.nameTo_lsFn(dn)
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
