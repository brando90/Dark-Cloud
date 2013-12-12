#!/usr/bin/env python

import httplib
import sys
import DCCryptoClient
import os

class DCClient:
    def __init__(self, username, passwd):
        self.username = None
        self.passwd = None
        self.wd = DCWorkingDirectory(self.username, self.passwd)
        self.HttpClient = DCHTTPClient("127.0.0.1", 8080)

    def tableFilename(self, name):
        return '.t-' + name

    def lsFilename(self, name):
        return '.ls-' + name

    def createFile(self, name, content):
        kfname = tableFilename(name)
        path = self.wd.toString()
        mkObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)

        keyObj = DCCryptoClient.createSecureKeyFile(self.username, self.passwd, kfname)
        encryptedKeyName = DCCryptoClient.encryptName(path + '/' + kfname, mkObj) #is this the right key
        encryptedName = DCCryptoClient.encryptName(path + '/' + name, keyObj)
        
        #request to read parent directory contents to add new files
        parentName = self.wd.up(1) # returns name of directory after the last slash
        #need to use lsfile here instead
        dirObj = readSecureDirObj(parentName)
        dirObj.add(encryptedKeyName, kfname)
        dirObj.add(encryptedName, name)
        dirObj.sort()

        #request to write the modified directory
        self.write(parentName, dirObj.content(), True)

        self.wd.down(parentName)

        #request to create key file on server
        
        encryptedPath = self.wd.encrypted_pwd() 
        secureKeyContent = keyObj.toSecureString(self.username, self.passwd, encryptedPath + '/' + encryptedKeyName)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedKeyName,
                                        True,
                                        False,
                                        secureKeyContent)

        #request to create regular file on server

        #need to encrypt empty string?
        secureFileContent = DCCryptoClient.encryptFile(content, keyObj)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedName,
                                        True,
                                        False,
                                        secureFileContent)

        #modify directory signature and send to server

        return "Created file: ", name

    def mkdir(self, args):
        name = args[0]
        lsname = lsFilename(name)
        kfname = tableFilename(name)
        path = self.wd.toString()
        mkObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)

        keyObj = DCCryptoClient.createSecureKeyFile(self.username, self.passwd, kfname)
        encryptedKeyName = DCCryptoClient.encryptName(path + '/' + kfname, mkObj) #is this the right key
        encryptedName = DCCryptoClient.encryptName(path + '/' + name, keyObj)
        encryptedLSFileName = DCCryptoClient.encryptName(lsname, keyObj)

        #request to read parent directory contents to add new directory
        parentName = self.wd.up(1) # returns name of directory after the last slash
        dirObj = readSecureDirObj(parentName)
        dirObj.add(encryptedKeyName, kfname)
        dirObj.add(encryptedName, name)
        dirObj.add(encryptedLSFileName, lsname)
        dirObj.sort()

        #request to write the modified directory
        self.write(parentName, dirObj.content(), True)

        self.wd.down(parentName)

        #request to create key file and directory on server
        
        encryptedPath = self.wd.encrypted_pwd()
        secureKeyContent = keyObj.toSecureString(self.username, self.passwd, encryptedPath + '/' + encryptedKeyName)

        #keyfile
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedKeyName,
                                        True,
                                        False,
                                        secureKeyContent)

        #lsfile
        secureFileContent = DCCryptoClient.encryptFile("", keyObj)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedDirectorySignature,
                                        True,
                                        False,
                                        secureFileContent)

        #directory
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedName,
                                        False,
                                        True)

        #modify parent directory signature and send to server


        return "Created directory: ", name

    def read(encryptedName):
        encryptedPath = self.wd.encrypted_pwd()
        content = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedKeyFileName)
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

    def readSecureDirObj(name):
        kfname = tableFilename(name)
        lsname = lsFilename(name)
        path = self.wd.toString()
        mkObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)

        #get encrypted keyfile name
        encryptedKeyFileName = DCCryptoClient.encryptName(path + '/' + kfname, mkObj)

        #TODO:check that keys exist for all parts of the encrypted path

        encryptedPath = self.wd.encrypted_pwd()

        #request keyfile
        secureKeyfileContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedKeyFileName)

        #construct key object
        keyObj = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd)

        #save keyobj for later
        DCCryptoClient.addKeyObj(path + '/' + lsname, keyObj)

        #request encrypted file using encrypted file name
        encryptedLSFileName = DCCryptoClient.encryptName(path + '/' + lsname, keyObj)
        encryptedDirName = DCCryptoClient.encryptName(path + '/' + name, keyObj)

        encryptedLSFileContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedLSFileName)
        dirContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedDirName)

        #decrypt file contents
        decryptedLSFileContent = DCCryptoClient.decryptFile(encryptedLSFileContent, keyObj)

        #verify contents
        dirObj = DCSecureDir(dirContent, decryptedLSFileContent)

        return dirObj
    
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
            secureKeyfileContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedKeyFileName)
            keyObj = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd, path + '/' + kfname)

        #encrypt file's new contents
        encryptedContent = DCCryptoClient.encryptFile(content, keyObj)

        #craft write request to server
        encryptedFileName = DCCryptoClient.encryptName(path + '/' + name, keyObj)
        encryptedPath = self.wd.encrypted_pwd()

        self.HttpClient.sendWriteRequest(encryptedPath + '/' + encryptedFileName,
                                         encryptedContent)

        return name + " written"

    def delete(name):
        kfname = tableFilename(name)
        path = self.wd.toString()
        mkObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)

        #------- request to delete key file ----------
        #get encrypted keyfile name
        encryptedKeyName = DCCryptoClient.encryptName(path + '/' + kfname, mkObj)
        encryptedPath = self.wd.encrypted_pwd()

        #request keyfile
        secureKeyfileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeyName)

        #construct key object
        keyObj = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd)

        #request encrypted file using encrypted file name
        encryptedFileName = DCCryptoClient.encryptName(path + '/' + name, keyObj)

        # -- request to change parent directory structure --
        #request to read parent directory contents to add new directory
        parentName = self.wd.up(1) # returns name of directory after the last slash
        dirObj = readSecureDirObj(parentName)
        dirObj.remove(encryptedKeyName, kfname)
        dirObj.remove(encryptedName, name)
        dirObj.sort()

        #request to write the modified directory
        self.write(parentName, dirObj.content(), True)

        self.wd.down(parentName)

        #---------- request to delete file -----------
        #delete keyfile
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedKeyName)

        #delete file
        self.HttpClient.sendDeleteRequest(encryptedPath + '/' + encryptedFileName)

        return

    def rmdir(args):
        name = args[0]
        kfname = tableFilename(name)
        lsname = lsFilename(name)
        path = self.wd.toString()
        mkObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)

        #------- request to delete key directory ----------
        #get encrypted keyfile name
        encryptedKeyName = DCCryptoClient.encryptName(path + '/' + kfname, mkObj)
        encryptedPath = self.wd.encrypted_pwd()

        #request keyfile
        secureKeyfileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeyName)

        #construct key object
        keyObj = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd)

        #request encrypted file using encrypted file name
        encryptedFileName = DCCryptoClient.encryptName(path + '/' + name, keyObj)
        encryptedLSFileName = DCCryptoClient.encryptName(path + '/' + lsname, keyObj)


        # -- request to change parent directory structure --
        #request to read parent directory contents to add new directory
        parentName = self.wd.up(1) # returns name of directory after the last slash
        dirObj = readSecureDirObj(parentName)
        dirObj.remove(encryptedKeyName, kfname)
        dirObj.remove(encryptedName, name)
        dirObj.remove(encryptedLSFileName, lsname)
        dirObj.sort()

        #request to write the modified directory
        self.write(parentName, dirObj.content(), True)

        self.wd.down(parentName)

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
        kfname = tableFilename(name)
        newKFName = tableFilename(newName)
        lsname = lsFilename(name)
        newLSName = lsFilename(lsname)
        path = self.wd.toString()
        mkObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + kfname)
        newMKObj = DCCryptoClient.createUserMasterKeyObj(self.username, self.passwd, path + '/' + newKFName)

        #TODO: check if name exists?
        #TODO: update keys in Key dictionary

        #------- get new encrypted names ----------
        #get encrypted keyfile name
        encryptedKeyName = DCCryptoClient.encryptName(path + '/' + kfname, mkObj)
        newEncryptedKeyName = DCCryptoClient.encryptName(path + '/' + newKFName, newMKObj)
        encryptedPath = self.wd.encrypted_pwd()

        #request keyfile
        secureKeyfileContent = self.HttpClient.sendReadRequest(encryptedPath + '/' + encryptedKeyName)

        #construct key object
        keyObj = DCCryptoClient.makeKeyFileObjFromSecureKeyData(secureKeyfileContent, self.username, self.passwd)

        #request encrypted file using encrypted file name
        encryptedFileName = DCCryptoClient.encryptName(path + '/' + name, keyObj)
        newEncryptedFileName = DCCryptoClient.encryptName(path + '/' + newName, keyObj)
        if isDir:
            encryptedLSFileName = DCCryptoClient.encryptName(path + '/' + lsname, keyObj)
            newEncryptedLSFileName = DCCryptoClient.encryptName(path + '/' + newLSName, keyObj)

        # -- request to change parent directory structure --
        #request to read parent directory contents to add new directory
        parentName = self.wd.up(1) # returns name of directory after the last slash
        dirObj = readSecureDirObj(parentName)
        dirObj.remove(encryptedKeyName, kfname)
        dirObj.remove(encryptedName, name)
        dirObj.add(newEncryptedFileName, newName)
        dirObj.add(newEncryptedKeyName, newKFName)
        if isDir:
            dirObj.remove(encryptedLSFileName, lsname)
            dirObj.add(newEncryptedLSFileName, newLSName)
        dirObj.sort()

        #request to write the modified directory
        self.write(parentName, dirObj.content(), True)

        self.wd.down(parentName)

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
        self.pwd = []

    def root():
        return '/' + self.username + '/'

    def up(steps=1):
        for i in range(0, steps):
            if len(self.pwd) != 0:
                self.pwd.pop()
            else:
                break

    def down(subdirectory):
        self.pwd.append(subdirectory)

    def pwd():
        return self.root() + '/'.join(self.pwd)

    def encrypted_pwd():
        for i in range(0,len(self.pwd)):
            dirname = self.pwd[0]
            path = self.root() + '/'.join(self.pwd[:i])
            # see if we can get the encrypted name without querying the server
            dirKey = dcCryptoClient.getKey(path)
            if not dirKey:
                # get encrypted keytable filename
                dirTableKey = DCTableKey(self.username, self.password, ktFilename(dirname))
                encryptedKTFilename = dcCryptoClient.encryptName(ktFilename(dirname))
                # query the server for the encrypted keytable file
                # decrypt the keytable file
                # store key object in crypto client
            
            dcCryptoClient.encryptName(dirname, dirKey)
            # encrypt dirname with key


            # otherwise, query the server for the keyfile
            # encrypt the name

# -----------------------------------


# *** Dark Cloud Secure Directory ***

class DCSecureDir:
    def __init__(self, directoryContents, lsContents):
        self.contents = directoryContents

    def add(encryptedName, plainTextName):
        pass

    def remove(plainTextName):
        pass

    def sort():
        pass

    def getLS():
        pass
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
