#!/usr/bin/env python

import httplib
import sys
from DCCryptoClient import *
import os
import urllib
from DCHTTPClient import *

GDCCryptoClient = DCCryptoClient()
GDCHTTPClient = DCHTTPClient('127.0.0.1', 8080)

def nameDecorator(name, encryptedName):
    return name + '-' + encryptedName

def keychainDecorator(name, encryptedKeychainName):
    return name+'Kc-'+encryptedKeychainName

def lsDecorator(name, encrypted_lsFn):
    return name + "_ls-"+ encrypted_lsFn

def keychainFn(name, username):
    print "kcFn name: %s, username: %s" % (name, username)
    return '.kc-' + username + '-' + name

def nameTo_lsFn(dirname):
    return '.ls-' + dirname

def register(username, passwd):
    print "registering username: %s, with password: %s" % (username, passwd)
    dn = username
    kcFn = keychainFn(dn, username)
    lsFn = nameTo_lsFn(dn)

    # keychain shouldn't exist yet

    userKeychain = GDCCryptoClient.createUserMasterKeyObj(username, passwd, '/'+kcFn)

    dirKeychain = GDCCryptoClient.createKeyFileObj('/'+username)
    encryptedDirKeychainFn = keychainDecorator(dn, GDCCryptoClient.encryptName('/'+kcFn, userKeychain))
    encryptedDn = nameDecorator(dn, GDCCryptoClient.encryptName('/'+dn, dirKeychain))
    encrypted_lsFn = lsDecorator(dn, GDCCryptoClient.encryptName('/'+lsFn, dirKeychain))

    secureKeychainContent = dirKeychain.toSecureString(username, passwd, '/'+kcFn)

    print "eDKcFn: " + urllib.quote(encryptedDirKeychainFn)

    #keyfile
    GDCHTTPClient.sendCreateRequest('/'+encryptedDirKeychainFn,
                                    True,
                                    False,
                                    secureKeychainContent)

    print "e_lsFn: " + urllib.quote(encrypted_lsFn)

    #lsfile
    secure_lsFileContent = dirKeychain.lock("")
    GDCHTTPClient.sendCreateRequest('/'+encrypted_lsFn,
                                    True,
                                    False,
                                    secure_lsFileContent)

    print "eDn: " + urllib.quote(encryptedDn)

    #directory
    print 
    GDCHTTPClient.sendCreateRequest('/'+encryptedDn,
                                    False,
                                    True)
    
    return DCClient(username, passwd)

class DCClient:
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd
        self.wd = DCWorkingDirectory(self.username, self.passwd)
        self.wd.down(username)

    def createFile(self, fn, content):
        print "createFile"
        kcFn = keychainFn(fn, self.username)
        pwd = self.wd.pwd()
        print "create file path: "+ pwd
        userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, pwd + kcFn)
        fileKeychain = GDCCryptoClient.createKeyFileObj(pwd + fn)

        encryptedFileKeychainFn = keychainDecorator(fn, GDCCryptoClient.encryptName(pwd + kcFn, userKeychain)) #is this the right key
        encryptedFn = nameDecorator(fn, GDCCryptoClient.encryptName(pwd + fn, fileKeychain))
        parentDn = self.wd.up(1) 
        print "parent Dirname = " + parentDn
        if parentDn:
            print "registering with parentDir: " + parentDn

            # username, password, dn, pwd, encrypted_pwd, httpClient
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.pwd(),self.wd.encrypted_pwd())
            print "verified dirkeychain"

            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            # encryptedFn, plaintextFn, encryptedFileKeychainFn, plaintextFileKeychainFn, httpClient
            dcdir.registerFile(encryptedFn, fn, encryptedFileKeychainFn, kcFn)
            print "pwd at parent dir: " + self.wd.pwd()
            self.wd.down(parentDn)
            print "pwd after cding back into dir: " + self.wd.pwd()

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
        print "pathsToKeys: " + repr(GDCCryptoClient.pathsToKeys)     
        encryptedPwd = self.wd.encrypted_pwd()
        print 'encryptedPwd: ' + encryptedPwd
        secureKeyContent = fileKeychain.toSecureString(self.username, self.passwd, encryptedPwd + encryptedFileKeychainFn)
        GDCHTTPClient.sendCreateRequest(encryptedPwd + encryptedFileKeychainFn,
                                        True,
                                        False,
                                        secureKeyContent)

        #request to create regular file on server

        #need to encrypt empty string?
        secureFileContent = GDCCryptoClient.encryptFile(content, fileKeychain)
        GDCHTTPClient.sendCreateRequest(encryptedPwd + encryptedFn,
                                        True,
                                        False,
                                        secureFileContent)

        return "Created file: ", fn

    def mkdir(self, name):
        print "mkdir"
        dn = name
        kcFn = keychainFn(dn, self.username)
        lsFn = nameTo_lsFn(dn)
        pwd = self.wd.pwd()

        userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, pwd + kcFn)

        dirKeychain = GDCCryptoClient.createKeyFileObj(pwd + dn)
        encryptedDirKeychainFn = keychainDecorator(dn, GDCCryptoClient.encryptName(pwd + kcFn, userKeychain)) #is this the right key
        encryptedDn = nameDecorator(dn, GDCCryptoClient.encryptName(pwd + dn, dirKeychain))
        encrypted_lsFn = lsDecorator(dn, GDCCryptoClient.encryptName(pwd + lsFn, dirKeychain)) # is the path needed??

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn,self.wd.pwd(), self.wd.encrypted_pwd())
            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            # plaintextDn, encryptedDn, plaintext_lsFn, encrypted_lsFn, plaintextFileKeychainFn, encryptedFileKeychainFn, httpClient
            dcdir.registerDir(encryptedDn, dn, encrypted_lsFn, lsFn, encryptedDirKeychainFn, kcFn)
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
        
        encryptedPwd = self.wd.encrypted_pwd()
        secureKeyContent = dirKeychain.toSecureString(self.username, self.passwd, encryptedPwd + encryptedDirKeychainFn)

        #keyfile
        GDCHTTPClient.sendCreateRequest(encryptedPwd + encryptedDirKeychainFn,
                                        True,
                                        False,
                                        secureKeyContent)

        #lsfile

        secureFileContent = GDCCryptoClient.encryptFile("", dirKeychain)
        GDCHTTPClient.sendCreateRequest(encryptedPwd + encrypted_lsFn,
                                        True,
                                        False,
                                        secureFileContent)

        print "newAccount: encryptedDn:" +encryptedDn

        #directory
        GDCHTTPClient.sendCreateRequest(encryptedPwd + encryptedDn,
                                        False,
                                        True)

        return "Created directory: ", name

    def read(self, encryptedName):
        encryptedPwd = self.wd.encrypted_pwd()
        content = GDCHTTPClient.sendReadRequest(encryptedPwd + encryptedName)
        return content

    def readFile(self,name):
        print "readFile"
        fn = name
        kcFn = keychainFn(fn, self.username)
        pwd = self.wd.pwd()
        
        fileKeychain = GDCCryptoClient.getKey(pwd + fn)
        if not fileKeychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, pwd + kcFn)

            #get encrypted keyfile name
            encryptedFileKeychainFn = keychainDecorator(fn, GDCCryptoClient.encryptedName(pwd + kcFn, userKeychain))

            secureKeyfileContent = self.read(encryptedFileKeychainFn)

            #construct key object
            fileKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, pwd + kcFn)

        #request encrypted file using encrypted file name
        encryptedFn = nameDecorator(fn, GDCCryptoClient.encryptName(pwd + fn, fileKeychain))

        encryptedFileContent = self.read(encryptedFn)

        #decrypt file contents
        decryptedFileContent = GDCCryptoClient.decryptFile(encryptedFileContent, fileKeychain)

        #verify contents

        return decryptedFileContent
    
    def readDir(self, name):
        print "readDir"
        dn = name
        kcFn = keychainFn(dn, self.username)
        lsFn = nameTo_lsFn(dn)
        pwd = self.wd.pwd()

        dirKeychain = GDCCryptoClient.getKey(pwd + dn)
        encryptedPwd = self.wd.encrypted_pwd()

        if not dirKeychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, pwd + kcFn)

            encryptedFileKeychainFn = keychainDecorator(dn, GDCCryptoClient.encryptName(pwd + kcFn, userKeychain))


            #request keyfile
            secureKeyContent = GDCHTTPClient.sendReadRequest(encryptedPwd + encryptedFileKeychainFn)

            #construct key object
            dirKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, pwd + kcFn)

        #request encrypted file using encrypted file name
        encrypted_lsFn = lsDecorator(dn, GDCCryptoClient.encryptName(pwd + lsFn, dirKeychain))
        encryptedDn = nameDecorator(dn, GDCCryptoClient.encryptName(pwd + dn, dirKeychain))

        encryptedLSFileContent = GDCHTTPClient.sendReadRequest(encryptedPwd + encrypted_lsFn)
        encryptedDirEntries = GDCHTTPClient.sendReadRequest(encryptedPwd + encryptedDn)

        #decrypt file contents
        lsFile = GDCCryptoClient.decryptFile(encryptedLSFileContent, dirKeychain)

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
        pwd = self.wd.pwd()
        
        userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, pwd + kcFn)

        #TODO: If file doesn't exist create it

        #get associated key for this file
        fileKeychain = GDCCryptoClient.getKey(pwd + fn)
        fileKeychain = GDCCryptoClient.getKey(pwd + fn)
        if not fileKeychain:
            #request keyfile
            encryptedKeychainFn = GDCCryptoClient.encryptName(pwd + kcFn, userKeychain)
            encryptedPwd = self.wd.encrypted_pwd()
            secureKeyfileContent = GDCHTTPClient.sendReadRequest(encryptedPwd + encryptedKeychainFn)
            fileKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, pwd + kcFn)

        #encrypt file's new contents
        encryptedContent = GDCCryptoClient.encryptFile(content, fileKeychain)

        #craft write request to server
        encryptedFn = GDCCryptoClient.encryptName(pwd + fn, fileKeychain)
        encryptedPwd = self.wd.encrypted_pwd()

        GDCHTTPClient.sendWriteRequest(encryptedPwd + encryptedFn,
                                         encryptedContent)

        return name + " written"

    def deleteFile(self, fn):
        print "deleteFile"
        kcFn = keychainFn(fn, self.username)
        pwd = self.wd.pwd()
        encryptedPwd = self.wd.encrypted_pwd()

        fileKeychain = GDCCryptoClient.getKey(pwd+fn)

        if not fileKeychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, pwd + kcFn)
            #------- request to delete key file ----------
            #get encrypted keyfile name
            encryptedFileKeychainFn = keychainDecorator(fn, GDCCryptoClient.encryptName(pwd + kcFn, userKeychain))

            #request keyfile
            secureKeychainContent = GDCHTTPClient.sendReadRequest(self.wd.encrypted_pwd() + encryptedFileKeychainFn)

            #construct key object
            fileKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeychainContent, self.username, self.passwd, path+'/'+kcFn)

        #request encrypted file using encrypted file name

        encryptedFn = nameDecorator(fn, GDCCryptoClient.encryptName(pwd + fn, fileKeychain))

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn,self.wd.pwd(), self.wd.encrypted_pwd())
            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            # 
            dcdir.unregisterFile(encryptedFn, encryptedFileKeychainFn)
            self.wd.down(parentDn)

        #---------- request to delete file -----------
        #delete keyfile
        GDCHTTPClient.sendDeleteRequest(encryptedPwd + encryptedFileKeychainFn)

        #delete file
        GDCHTTPClient.sendDeleteRequest(encryptedPwd + encryptedFn)

        return

    # rmdir => dirs only
    def rmdir(self, args):
        print "rmdir"
        dn = args[0]
        kcFn = keychainFn(dn, self.username)
        lsFn = nameTo_lsFn(name)
        pwd = self.wd.pwd()

        dirKeychain = GDCCryptoClient.getKey(pwd + dn)

        if not dirKeychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, pwd + kcFn)

            #------- request to delete key directory ----------
            #get encrypted keyfile name
            encryptedKeychainFn = keychainDecorator(dn, GDCCryptoClient.encryptName(pwd + kcFn, userKeychain))
            encryptedPwd = self.wd.encrypted_pwd()

            #request keyfile
            secureKeyfileContent = GDCHTTPClient.sendReadRequest(encryptedPwd + encryptedKeychainFn)

            #construct key object
            dirKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, pwd + kcFn)

        #request encrypted file using encrypted file name
        encryptedDn = nameDecorator(dn, GDCCryptoClient.encryptName(pwd + dn, dirKeychain))
        encrypted_lsFn = lsDecorator(dn, GDCCryptoClient.encryptName(pwd + lsFn, dirKeychain))

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.pwd(),self.wd.encrypted_pwd())
            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            # plaintextDn, encryptedDn, plaintext_lsFn, encrypted_lsFn, plaintextDirKeychainFn, encryptedDirKeychainFn, httpClient
            dcdir.unregisterDir(encryptedDn, encrypted_lsFn, encryptedDirKeychainFn)
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
        GDCHTTPClient.sendDeleteRequest(encryptedPwd + encryptedKeychainFn)

        #delete file
        GDCHTTPClient.sendDeleteRequest(encryptedPwd + encryptedDn)

        #delete ls file
        GDCHTTPClient.sendDeleteRequest(encryptedPwd + encrypted_lsFn)

        return

    def rename(self, name, newName, isDir=False):
        print "rename"
        kcFn = keychainFn(name, self.username)
        newKcFn = keychainFn(newName, self.username)
        lsFn = lsFilename(name)
        new_lsFn = lsFilename(newName)
        pwd = self.wd.pwd()
        encryptedPwd = self.wd.encrypted_pwd()

        keychain = GDCCryptoClient.getKey(pwd + name)
        if not keychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, pwd + kcFn)
            encryptedKeychainFn = keychainDecorator(name, GDCCryptoClient.encryptName(pwd + kcFn, userKeychain))
            #request keyfile
            secureKeychainContent = GDCHTTPClient.sendReadRequest(encryptedPwd + encryptedKeychainFn)
            #construct key object
            keychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeychainContent, self.username, self.passwd, pwd + kcFn)
        

        newUserKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, pwd + newKcFn)

        #get encrypted keyfile name
        newEncryptedKeychainFn = keychainDecorator(newName, GDCCryptoClient.encryptName(pwd + newKcFn, newUserKeychain))

        #request encrypted file using encrypted file name
        encryptedName = nameDecorator(name, GDCCryptoClient.encryptName(pwd + name, keychain))
        newEncryptedName = nameDecorator(newName, GDCCryptoClient.encryptName(pwd + newName, keychain))
        encrypted_lsFn = None
        newEncrypted_lsFn = None
        if isDir:
            encrypted_lsFn = lsDecorator(name, GDCCryptoClient.encryptName(pwd + lsFn, keychain))
            newEncrypted_lsFn = lsDecorator(newName, GDCCryptoClient.encryptName(pwd + new_lsFn, keychain))

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.pwd(),self.wd.encrypted_pwd())
            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            
            if isDir: # renaming a dir
                # Unregisted encryptedDn, encryptedKeychainFn, encrypted_lsFn
                dcdir.unregisterDir(encryptedName, encryptedPwd)
                # Register newEncryptedDn, newPlaintextDn, newEncryptedKeychainFn, newPlaintextKeychainFn, newEncrypted_lsFn, new_lsFn httpClient
                dcdir.registerDir(newEncryptedName, newName, newEncryptedKeychainFn, newKcFn, newEncrypted_lsFn, new_lsFn)
            else: # renaming a file
                # Unregisted encryptedName, encryptedKeychainFn
                dcdir.unregisterFile(encryptedName, encryptedKeychainFn)
                # Register newEncryptedFn, newPlaintextFn, newEncryptedKeychainFn, newPlaintextKeychainFn, httpClient
                dcdir.registerFile(newEncryptedName, newName, newEncryptedKeychainFn, newKcFn)
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
        GDCHTTPClient.sendReadRequest(encryptedPwd + encryptedName,
                                        encryptedPwd + newEncryptedName)
        GDCHTTPClient.sendReadRequest(encryptedPwd + encryptedKeychainFn,
                                        encryptedPwd + newEncryptedKeychainFn)
        if isDir:
            GDCHTTPClient.sendReadRequest(encryptedPwd + encrypted_lsFn,
                                            encryptedPwd + newEncrypted_lsFn)

# -------------------------------


# *** Working Directory Class ***

class DCWorkingDirectory:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.directoryStack = []

    def encryptedRoot(self):
        kcFn = keychainFn(self.username, self.username)
        print "username: %s, password: %s" % (self.username, self.password)

        userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.password, kcFn)
        encryptedFileKeychainFn = GDCCryptoClient.encryptName(kcFn, userKeychain)
        #print "trying to access eFKcFn: " + urllib.quote(keychainDecorator(self.username,encryptedFileKeychainFn))
        secureRootKeychain = GDCHTTPClient.sendReadRequest(keychainDecorator(self.username,encryptedFileKeychainFn))
        rootKeychain =  GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureRootKeychain, self.username, self.password, self.pwd() +'/'+kcFn)
        encryptedRoot = GDCCryptoClient.encryptName(self.username,rootKeychain)
        print "Encrypted ROOT: " + encryptedRoot

        return encryptedRoot

    def up(self,steps=1):

        newWD = None
        for i in xrange(0, steps):
            if len(self.directoryStack) > 0:
                newWD = self.directoryStack.pop()
            else:
                return '/'
        return newWD

    def down(self,subdirectory):
        self.directoryStack.append(subdirectory)

    def path(self,directories):
        #print "path: " + self.currentRoot + '/'.join(directories)
        if len(directories) == 0:
            return '/'
        else:
            return '/' + '/'.join(directories) + '/'

    def pwd(self):
        return self.path(self.directoryStack)

    def encrypted_pwd(self):
        print "encrypting pwd: " + self.pwd()
        print "saved keychains: " + repr(GDCCryptoClient.pathsToKeys)
        encrypted_pwd = []
        for i in range(0,len(self.directoryStack)):
            dirname = self.directoryStack[i]
            path = self.path(self.directoryStack[:i]) + dirname
            # see if we can get the encrypted name without querying the server
            print 'path: '+path
            dirKey = GDCCryptoClient.getKey(path)
            if not dirKey:
               raise ValueError("cd'ing through multiple directories at once is not yet implemented. Must manually cd through them.")

            # encrypt dirname with key            
            encryptedDirname = GDCCryptoClient.encryptName(path, dirKey)
            encrypted_pwd.append(nameDecorator(dirname, encryptedDirname))
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
    def verifiedDirKeychain(username, password, dn, pwd, encrypted_pwd):
        kcFn = keychainFn(dn, username)
        print "verifiedDirKeychain"
        print '*** pwd: %s, encrypted_pwd:%s, dn: %s' % (pwd, encrypted_pwd, dn)
        userKeychain = GDCCryptoClient.createUserMasterKeyObj(username, password,  pwd + kcFn)
        # Get encrypted dirKeychainFn name
        encryptedDirKeychainFn = GDCCryptoClient.encryptName(pwd + kcFn, userKeychain)
        # Query server for secure dirKeychain
        print "READ REQUEST: encrypted_pwd:%s, encryptedDirKeychainFn:%s" % (encrypted_pwd, keychainDecorator(dn,urllib.quote(encryptedDirKeychainFn)))
        secureDirKeychain = GDCHTTPClient.sendReadRequest(encrypted_pwd + keychainDecorator(dn,encryptedDirKeychainFn))
        # Unlock dirKeychain and return it
        # secureKeyFileData, username, password, keyFileName
        return GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureDirKeychain, username, password, pwd + kcFn)

    @staticmethod
    def sorted_lsEntries(lsFile):
        entries = []
        offset = 0
        while offset < len(lsFile):
            entry, newOffset = DCDir.readEntry(lsFile, offset)
            entries.append(entry)
            offset = newOffset
        # Sort by encrypted entry names
        sorted_entries = sorted(entries, key=lambda entry: entry.encryptedName)
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

    def __init__(self, dn, pwd, encryptedPwd, dirKeychain): # how should this be initialized
        self.dn = dn
        self.encryptedDirname = GDCCryptoClient.encryptName(dn, dirKeychain)
        self.encryptedPwd = encryptedPwd
        self.lsFn = DCDir.nameTo_lsFn(dn)
        self.encrypted_lsFn = GDCCryptoClient.encryptName(pwd + self.lsFn, dirKeychain)
        self.dirKeychain = dirKeychain
    
    def fullEncryptedPath(self, name):
        full_enc_path = self.encryptedPwd + name
        print "full_enc_path: " + urllib.quote(full_enc_path)
        return full_enc_path

    # Add file to directory ls file
    def registerFile(self,encryptedFn, plaintextFn, encryptedFileKeychainFn, plaintextFileKeychainFn):
        #TODO: unlock & lock? or method for this in cryptclient
        # - Query server for secure ls file
        secure_lsFile = GDCHTTPClient.sendReadRequest(self.fullEncryptedPath(lsDecorator(self.dn ,self.encrypted_lsFn)))
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
        return GDCHTTPClient.sendWriteRequest(self.fullEncryptedPath(lsDecorator(self.dn,self.encrypted_lsFn)), updatedSecure_lsFile)

    # Remove file from directory ls file
    def unregisterFile(self,encryptedFn, encryptedFileKeychainFn):
        # - Query server for secure ls file
        secure_lsFile = GDCHTTPClient.sendReadRequest(self.fullEncryptedPath(lsDecorator(self.dn,self.encrypted_lsFn)))
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
        return GDCHTTPClient.sendWriteRequest(self.fullEncryptedPath(lsDecorator(self.dn, self.encrypted_lsFn)), updatedSecure_lsFile)

    # Add dir to directory ls file
    def registerDir(self,encryptedDn, plaintextDn, encrypted_lsFn, plaintext_lsFn, encryptedDirKeychainFn, plaintextDirKeychainFn):
        # - Query server for secure ls file
        secure_lsFile = GDCHTTPClient.sendReadRequest(self.fullEncryptedPath(lsDecorator(self.dn, self.encrypted_lsFn)))
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
        return GDCHTTPClient.sendWriteRequest(self.fullEncryptedPath(lsDecorator(self.dn, self.encrypted_lsFn)), updatedSecure_lsFile)

    # Remove dir from directory ls file
    def unregisterDir(self,encryptedDn, encrypted_lsFn, encryptedDirKeychainFn):
        # - Query server for secure ls file
        secure_lsFile = GDCHTTPClient.sendReadRequest(self.fullEncryptedPath(lsDecorator(self.dn, self.encrypted_lsFn)))
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
        return GDCHTTPClient.sendWriteRequest(self.fullEncryptedPath(lsDecorator(self.dn, self.encrypted_lsFn)), updatedSecure_lsFile)

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
    print "Correct DCClient implementation"
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
