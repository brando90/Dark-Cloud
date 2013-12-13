#!/usr/bin/env python

import httplib
import sys
from DCCryptoClient import *
import os
import urllib
from DCHTTPClient import *

GDCCryptoClient = DCCryptoClient()
GDCHTTPClient = DCHTTPClient('127.0.0.1', 8080)

DEBUG = True

def nameDecorator(name, encryptedName):
    if DEBUG:
        return name + '-' + encryptedName
    else:
        return encryptedName

def keychainDecorator(name, encryptedKeychainName):
    if DEBUG:
        return name+'Kc-'+encryptedKeychainName
    else:
        return encryptedKeychainName

def lsDecorator(name, encrypted_lsFn):
    if DEBUG:
        return name + "_ls-"+ encrypted_lsFn
    else:
        return encrypted_lsFn

def keychainFn(name, username):
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
        enc_pwd = self.wd.encrypted_pwd()
        print "create file path: "+ pwd
        userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)
        fileKeychain = GDCCryptoClient.createKeyFileObj(urllib.quote(enc_pwd) + fn)

        encryptedFileKeychainFn = keychainDecorator(fn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain)) #is this the right key
        encryptedFn = nameDecorator(fn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + fn, fileKeychain))
        parentDn = self.wd.up(1) 
        print "parent Dirname = " + parentDn
        if parentDn:
            print "registering with parentDir: " + parentDn

            # username, password, dn, pwd, encrypted_pwd, httpClient
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn,self.wd.encrypted_pwd())
            print "verified dirkeychain"

            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            # encryptedFn, plaintextFn, encryptedFileKeychainFn, plaintextFileKeychainFn, httpClient
            dcdir.registerFile(encryptedFn, fn, encryptedFileKeychainFn, kcFn)
            print "pwd at parent dir: " + self.wd.pwd()
            self.wd.down(parentDn)
            print "pwd after cding back into dir: " + self.wd.pwd()

        #request to create key file on server   
        print "pathsToKeys: " + repr(GDCCryptoClient.pathsToKeys)     
        print 'enc_pwd: ' + enc_pwd
        secureKeyContent = fileKeychain.toSecureString(self.username, self.passwd, urllib.quote(enc_pwd) + encryptedFileKeychainFn)
        GDCHTTPClient.sendCreateRequest(enc_pwd + encryptedFileKeychainFn,
                                        True,
                                        False,
                                        secureKeyContent)

        #request to create regular file on server

        #need to encrypt empty string?
        secureFileContent = GDCCryptoClient.encryptFile(content, fileKeychain)
        GDCHTTPClient.sendCreateRequest(enc_pwd + encryptedFn,
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
        enc_pwd = self.wd.encrypted_pwd()

        userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)

        dirKeychain = GDCCryptoClient.createKeyFileObj(urllib.quote(enc_pwd) + dn)
        encryptedDirKeychainFn = keychainDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain)) #is this the right key
        encryptedDn = nameDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + dn, dirKeychain))
        encrypted_lsFn = lsDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + lsFn, dirKeychain)) # is the path needed??

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.encrypted_pwd())
            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            # plaintextDn, encryptedDn, plaintext_lsFn, encrypted_lsFn, plaintextFileKeychainFn, encryptedFileKeychainFn, httpClient
            dcdir.registerDir(encryptedDn, dn, encrypted_lsFn, lsFn, encryptedDirKeychainFn, kcFn)
            self.wd.down(parentDn)

        #request to create key file and directory on server
        
        secureKeyContent = dirKeychain.toSecureString(self.username, self.passwd, urllib.quote(enc_pwd) + encryptedDirKeychainFn)

        #keyfile
        GDCHTTPClient.sendCreateRequest(enc_pwd + encryptedDirKeychainFn,
                                        True,
                                        False,
                                        secureKeyContent)

        #lsfile

        secureFileContent = GDCCryptoClient.encryptFile("", dirKeychain)
        GDCHTTPClient.sendCreateRequest(enc_pwd + encrypted_lsFn,
                                        True,
                                        False,
                                        secureFileContent)

        print "newAccount: encryptedDn:" +encryptedDn

        #directory
        GDCHTTPClient.sendCreateRequest(enc_pwd + encryptedDn,
                                        False,
                                        True)

        return "Created directory: ", name

    def read(self, encryptedName):
        print "read encryptedName: " + encryptedName
        enc_pwd = self.wd.encrypted_pwd()
        content = GDCHTTPClient.sendReadRequest(enc_pwd + encryptedName)
        return content

    def readFile(self,name):
        print "readFile"
        fn = name
        kcFn = keychainFn(fn, self.username)
        pwd = self.wd.pwd()
        enc_pwd = self.wd.encrypted_pwd()
        
        fileKeychain = GDCCryptoClient.getKey(urllib.quote(enc_pwd) + fn)
        if not fileKeychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)

            #get encrypted keyfile name
            encryptedFileKeychainFn = keychainDecorator(fn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain))

            print "readFile eFKcFn: " + encryptedFileKeychainFn

            secureKeyfileContent = self.read(encryptedFileKeychainFn)

            #construct key object
            fileKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)

        print "fKc: " + str(fileKeychain)

        #request encrypted file using encrypted file name
        encryptedFn = nameDecorator(fn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + fn, fileKeychain))

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
        enc_pwd = self.wd.encrypted_pwd()

        dirKeychain = GDCCryptoClient.getKey(urllib.quote(enc_pwd) + dn)

        if not dirKeychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)

            encryptedFileKeychainFn = keychainDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain))


            #request keyfile
            secureKeychainContent = GDCHTTPClient.sendReadRequest(urllib.quote(enc_pwd) + encryptedFileKeychainFn)

            #construct key object
            dirKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeychainContent, self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)

        #request encrypted file using encrypted file name
        encrypted_lsFn = lsDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + lsFn, dirKeychain))
        encryptedDn = nameDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + dn, dirKeychain))

        encryptedLSFileContent = GDCHTTPClient.sendReadRequest(urllib.quote(enc_pwd) + encrypted_lsFn)
        encryptedDirEntries = GDCHTTPClient.sendReadRequest(urllib.quote(enc_pwd) + encryptedDn)

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
        enc_pwd = self.wd.encrypted_pwd()
        
        userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)

        #TODO: If file doesn't exist create it

        #get associated key for this file
        fileKeychain = GDCCryptoClient.getKey(urllib.quote(enc_pwd) + fn)
        fileKeychain = GDCCryptoClient.getKey(urllib.quote(enc_pwd) + fn)
        if not fileKeychain:
            #request keyfile
            encryptedKeychainFn = keychainDecorator(fn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain))
            secureKeyfileContent = GDCHTTPClient.sendReadRequest(encryptedPwd + encryptedKeychainFn)
            fileKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)

        #encrypt file's new contents
        encryptedContent = GDCCryptoClient.encryptFile(content, fileKeychain)

        #craft write request to server
        encryptedFn = nameDecorator(fn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + fn, fileKeychain))
        encryptedPwd = self.wd.encrypted_pwd()

        GDCHTTPClient.sendWriteRequest(enc_pwd + encryptedFn,
                                         encryptedContent)

        return name + " written"

    def deleteFile(self, fn):
        print "deleteFile"
        kcFn = keychainFn(fn, self.username)
        pwd = self.wd.pwd()
        enc_pwd = self.wd.encrypted_pwd()

        fileKeychain = GDCCryptoClient.getKey(urllib.quote(enc_pwd)+fn)
        encryptedFileKeychainFn = None
        if not fileKeychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)
            #------- request to delete key file ----------
            #get encrypted keyfile name
            encryptedFileKeychainFn = keychainDecorator(fn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain))

            #request keyfile
            secureKeychainContent = GDCHTTPClient.sendReadRequest(self.wd.encrypted_pwd() + encryptedFileKeychainFn)

            #construct key object
            fileKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeychainContent, self.username, self.passwd, urllib.quote(enc_pwd)+kcFn)

        #request encrypted file using encrypted file name

        encryptedFn = nameDecorator(fn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + fn, fileKeychain))

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn, self.wd.encrypted_pwd())
            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            # 
            if not encryptedFileKeychainFn:
                userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)
                encryptedFileKeychainFn = keychainDecorator(fn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain))
            dcdir.unregisterFile(encryptedFn, encryptedFileKeychainFn)
            self.wd.down(parentDn)

        #---------- request to delete file -----------
        #delete keyfile
        GDCHTTPClient.sendDeleteRequest(enc_pwd + encryptedFileKeychainFn)

        #delete file
        GDCHTTPClient.sendDeleteRequest(enc_pwd + encryptedFn)

        return

    # rmdir => dirs only
    def rmdir(self, dn):
        print "rmdir"
        kcFn = keychainFn(dn, self.username)
        lsFn = nameTo_lsFn(dn)
        pwd = self.wd.pwd()
        enc_pwd = self.wd.encrypted_pwd()

        dirKeychain = GDCCryptoClient.getKey(urllib.quote(enc_pwd) + dn)

        encryptedDirKeychainFn = None

        if not dirKeychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)

            #------- request to delete key directory ----------
            #get encrypted keyfile name
            encryptedDirKeychainFn = keychainDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain))

            #request keyfile
            secureKeyfileContent = GDCHTTPClient.sendReadRequest(enc_pwd + encryptedDirKeychainFn)

            #construct key object
            dirKeychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)

        #request encrypted file using encrypted file name
        encryptedDn = nameDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + dn, dirKeychain))
        encrypted_lsFn = lsDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + lsFn, dirKeychain))

        parentDn = self.wd.up(1)
        if parentDn:
            if not encryptedDirKeychainFn:
                userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)
                encryptedDirKeychainFn = keychainDecorator(dn, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain))
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn,self.wd.encrypted_pwd())
            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            # plaintextDn, encryptedDn, plaintext_lsFn, encrypted_lsFn, plaintextDirKeychainFn, encryptedDirKeychainFn, httpClient
            dcdir.unregisterDir(encryptedDn, encrypted_lsFn, encryptedDirKeychainFn)
            self.wd.down(parentDn)

        #---------- request to delete directory -----------
        #delete keyfile
        GDCHTTPClient.sendDeleteRequest(enc_pwd + encryptedDirKeychainFn)

        #delete file
        GDCHTTPClient.sendDeleteRequest(enc_pwd + encryptedDn)

        #delete ls file
        GDCHTTPClient.sendDeleteRequest(enc_pwd + encrypted_lsFn)

        return

    def rename(self, name, newName, isDir=False):
        print "rename"
        kcFn = keychainFn(name, self.username)
        newKcFn = keychainFn(newName, self.username)
        lsFn = nameTo_lsFn(name)
        new_lsFn = nameTo_lsFn(newName)
        pwd = self.wd.pwd()
        enc_pwd = self.wd.encrypted_pwd()

        keychain = GDCCryptoClient.getKey(urllib.quote(enc_pwd) + name)
        encryptedKeychainFn = None
        if not keychain:
            userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)
            encryptedKeychainFn = keychainDecorator(name, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain))
            #request keyfile
            secureKeychainContent = GDCHTTPClient.sendReadRequest(urllib.quote(enc_pwd) + encryptedKeychainFn)
            #construct key object
            keychain = GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeychainContent, self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)
        

        newUserKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + newKcFn)

        #get encrypted keyfile name
        newEncryptedKeychainFn = keychainDecorator(newName, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + newKcFn, newUserKeychain))

        #request encrypted file using encrypted file name
        encryptedName = nameDecorator(name, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + name, keychain))
        newEncryptedName = nameDecorator(newName, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + newName, keychain))
        encrypted_lsFn = None
        newEncrypted_lsFn = None
        print 'isDir? : ' + str(isDir)
        if isDir:
            encrypted_lsFn = lsDecorator(name, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + lsFn, keychain))
            newEncrypted_lsFn = lsDecorator(newName, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + new_lsFn, keychain))

        parentDn = self.wd.up(1)
        if parentDn:
            parentDirKeychain = DCDir.verifiedDirKeychain(self.username, self.passwd, parentDn,self.wd.encrypted_pwd())
            # Initialize dcdir with: parentDn, pwd, encrypted_pwd, parentDirKeychain
            dcdir = DCDir(parentDn, self.wd.pwd(), self.wd.encrypted_pwd(), parentDirKeychain)
            if not encryptedKeychainFn:
                    userKeychain = GDCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, urllib.quote(enc_pwd) + kcFn)
                    encryptedKeychainFn = keychainDecorator(name, GDCCryptoClient.encryptName(urllib.quote(enc_pwd) + kcFn, userKeychain))
            if isDir: # renaming a dir
                # Unregisted encryptedDn, encryptedKeychainFn, encrypted_lsFn

                dcdir.unregisterDir(encryptedName, encrypted_lsFn, encryptedKeychainFn)
                # Register newEncryptedDn, newPlaintextDn, newEncryptedKeychainFn, newPlaintextKeychainFn, newEncrypted_lsFn, new_lsFn httpClient
                dcdir.registerDir(newEncryptedName, newName, newEncryptedKeychainFn, newKcFn, newEncrypted_lsFn, new_lsFn)
            else: # renaming a file
                # Unregisted encryptedName, encryptedKeychainFn
                dcdir.unregisterFile(encryptedName, encryptedKeychainFn)
                # Register newEncryptedFn, newPlaintextFn, newEncryptedKeychainFn, newPlaintextKeychainFn, httpClient
                dcdir.registerFile(newEncryptedName, newName, newEncryptedKeychainFn, newKcFn)
            self.wd.down(parentDn)

        # -------- set new names -------------------
        GDCHTTPClient.sendRenameRequest(enc_pwd + encryptedName,
                                        enc_pwd + newEncryptedName)
        GDCHTTPClient.sendRenameRequest(enc_pwd + encryptedKeychainFn,
                                        enc_pwd + newEncryptedKeychainFn)
        if isDir:
            GDCHTTPClient.sendRenameRequest(enc_pwd + encrypted_lsFn,
                                            enc_pwd + newEncrypted_lsFn)

# -------------------------------


# *** Working Directory Class ***

class DCWorkingDirectory:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.directoryStack = []

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
        print "Adding dir entry: lsFile:%s, ptFn:%s, eFn:%s" % (lsFile, plaintextFn, encryptedFn)

        ptFnLength = len(plaintextFn)
        encFnLength = len(urllib.quote(encryptedFn))
        lengthlessEntry = 'fn,' + str(ptFnLength) + ',' + str(encFnLength) + ',' + plaintextFn + ',' + urllib.quote(encryptedFn) + ';'
        entryLength = len(lengthlessEntry) + 1 # comma (below) takes one character
        entry = str(entryLength) + ',' + lengthlessEntry
        return lsFile + entry

    @staticmethod
    def removeFile_lsEntry(lsFile, encryptedFn):
        offset = 0
        updated_lsFile = None
        while offset < len(lsFile):
            entry, newOffset = DCDir.readEntry(lsFile, offset)
            print "Entry encrypted name: " + entry.encryptedName
            print "matches query: %s?" % encryptedFn
            print "isFile? : " + str(entry.isFile)
            if entry.isFile and (entry.encryptedName == encryptedFn):
                #remove entry
                print "Entry removed!"
                updated_lsFile = lsFile[:offset] + lsFile[newOffset:]
            offset = newOffset
        return updated_lsFile

        

    @staticmethod
    def addDir_lsEntry(lsFile, plaintextDn, encryptedDn):
        # Entry looks as follows: 
        #   entryLength,fn/dn,ptNameLength,encNameLength,ptName,encName;
        print "Adding dir entry: lsFile:%s, ptDn:%s, eDn:%s" % (lsFile, plaintextDn, encryptedDn)
        ptDnLength = len(plaintextDn)
        encDnLength = len(urllib.quote(encryptedDn))
        lengthlessEntry = 'dn,' + str(ptDnLength) + ',' + str(encDnLength) + ',' + plaintextDn + ',' + urllib.quote(encryptedDn) + ';'
        entryLength = len(lengthlessEntry) + 1 # comma (below) takes one character
        entry = str(entryLength) + ',' + lengthlessEntry
        return lsFile + entry
        

    @staticmethod
    def removeDir_lsEntry(lsFile, encryptedDn):
        offset = 0
        updated_lsFile = None
        while offset < len(lsFile):
            entry, newOffset = DCDir.readEntry(lsFile, offset)
            print "Entry encrypted name: " + entry.encryptedName
            print "matches query: %s?" % encryptedDn
            print "entry is dir? : " + str(entry.isDir)
            if entry.isDir and (entry.encryptedName == encryptedDn):
                #remove entry
                print "Entry removed!"
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
                    print "stringBuilder found: " + stringBuilder
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
    def verifiedDirKeychain(username, password, dn, encrypted_pwd):
        kcFn = keychainFn(dn, username)
        print "verifiedDirKeychain"
        print '*** encrypted_pwd:%s, dn: %s' % (encrypted_pwd, dn)
        userKeychain = GDCCryptoClient.createUserMasterKeyObj(username, password,  encrypted_pwd + kcFn)
        # Get encrypted dirKeychainFn name
        encryptedDirKeychainFn = keychainDecorator(dn, GDCCryptoClient.encryptName(encrypted_pwd + kcFn, userKeychain))
        # Query server for secure dirKeychain
        print "READ REQUEST: encrypted_pwd:%s, encryptedDirKeychainFn:%s" % (encrypted_pwd, keychainDecorator(dn,urllib.quote(encryptedDirKeychainFn)))
        secureDirKeychain = GDCHTTPClient.sendReadRequest(encrypted_pwd + encryptedDirKeychainFn)
        # Unlock dirKeychain and return it
        # secureKeyFileData, username, password, keyFileName
        return GDCCryptoClient.makeKeyFileObjFromSecureKeyData(secureDirKeychain, username, password, encrypted_pwd + kcFn)

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
        print "VERIFYING WITH LS:"
        
        encrypted_lsFileEntries = []
        offset = 0
        while offset < len(lsFile):
            lsFileEntry, newOffset = DCDir.readEntry(lsFile, offset)
            encrypted_lsFileEntries.append(lsFileEntry)
            offset = newOffset

        sortedEncrypted_lsFileEntries = sorted(encrypted_lsFileEntries, key=lambda lsEntry: lsEntry.encryptedName)
        print "LS_FILE_ENTRIES: " + repr([entry.encryptedName for entry in sortedEncrypted_lsFileEntries])
        print "ENC_DIR_CONTENTS: " + repr(sortedEncryptedDirEntries)
        
        if len(sortedEncryptedDirEntries) != len(sortedEncrypted_lsFileEntries):
            raise ValueError("DCDir verification failed!")

        plaintextEntryNames = []
        for i in xrange(0, len(sortedEncryptedDirEntries)):
            encryptedNameFromDir = sortedEncryptedDirEntries[i]
            lsEntry = sortedEncrypted_lsFileEntries[i]
            if (encryptedNameFromDir != lsEntry.encryptedName):
                # Mismatch in sorted entries
                raise ValueError("DCDir verification failed!")
            plaintextEntryNames.append(lsEntry.plaintextName)       
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
        print "lsFile after add file and sorting: " + updatedSorted_lsFile
        updatedSecure_lsFile = self.dirKeychain.lock(updatedSorted_lsFile)
        # - Query server to overwrite secure ls file
        return GDCHTTPClient.sendWriteRequest(self.fullEncryptedPath(lsDecorator(self.dn,self.encrypted_lsFn)), updatedSecure_lsFile)

    # Remove file from directory ls file
    def unregisterFile(self,encryptedFn, encryptedFileKeychainFn):
        # - Query server for secure ls file
        secure_lsFile = GDCHTTPClient.sendReadRequest(self.fullEncryptedPath(lsDecorator(self.dn,self.encrypted_lsFn)))
        # - Unlock (decrypt/verify) ls file
        lsFile = self.dirKeychain.unlock(secure_lsFile)
        print "lsFile: "+ lsFile
        # - Update ls file by removing filename and fileKeychain name (plaintext & encrypted name)
        lsFile_file = DCDir.removeFile_lsEntry(lsFile, urllib.quote(encryptedFn))
        print "lsFile_file: "+lsFile_file
        lsFile_file_keychain = DCDir.removeFile_lsEntry(lsFile_file, urllib.quote(encryptedFileKeychainFn))
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
        print "updated lsFile after added dir: " + lsFile_dir_ls_keychain
        # - Sort updated ls file
        updatedSorted_lsFile = DCDir.sorted_lsEntries(lsFile_dir_ls_keychain)
        # - Secure (sign/encrypt) updated, sorted ls file
        print "after sorting: " + updatedSorted_lsFile
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
        lsFile_dir = DCDir.removeDir_lsEntry(lsFile, urllib.quote(encryptedDn))
        lsFile_dir_ls = DCDir.removeFile_lsEntry(lsFile_dir, urllib.quote(encrypted_lsFn))
        lsFile_dir_ls_keychain = DCDir.removeFile_lsEntry(lsFile_dir_ls, urllib.quote(encryptedDirKeychainFn))
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
        lengthlessEntry = fnSlashDn + ',' + str(ptNameLength) + ',' + str(encNameLength) + ',' + self.plaintextName + ',' + self.encryptedName + ';'
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
