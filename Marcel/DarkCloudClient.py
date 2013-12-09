#!/usr/bin/env python

import httplib
import sys
import DCCryptoClient
import os


class CommandError(Exception):
    pass


class DCClient:
    def __init__():
        self.username = None
        self.passwd = None
        self.wd = None
        self.HttpClient = DCHTTPClient(127.0.0.1, 8080)

    def createFile(args):
        name = args[0]

        #request to read parent directory contents to add new files

        #request to create key file on server
        keyfile = DCCryptoClient.createSecureKeyFile(self.username, self.passwd, '.kf-' + name)
        encryptedKeyName = DCCryptoClient.encryptKeyFileName('.kf-' + name, self.passwd)
        encryptedPath = DCCryptoClient.encryptPath(self.wd)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedKeyName,
                                        True,
                                        False,
                                        keyfile)

        #request to create regular file on server
        encryptedName = DCCryptoClient.encryptName(name, keyfile)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedName,
                                        True,
                                        False,
                                        "")

        #modify directory signature and send to server

        return "Created file: ", name

    def mkdir(args):
        name = args[0]

        #request to change parent directory contents
        parentDirContents = readDir(self.wd)

        #request to create key file and directory on server
        keyfile = DCCryptoClient.createSecureKeyFile(self.username, self.passwd, '.kf-' + name)
        encryptedKeyName = DCCryptoClient.encryptKeyFileName('.kf-' + name, self.passwd)
        encryptedName = DCCryptoClient.encryptName(name, keyfile)
        encryptedPath = DCCryptoClient.encryptPath(self.wd)

        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedKeyName,
                                        True,
                                        False,
                                        keyfile)
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedDirectorySignature,
                                        True,
                                        False,
                                        )
        self.HttpClient.sendCreateRequest(encryptedPath + '/' + encryptedName,
                                        False,
                                        True)

        #modify parent directory signature and send to server


        return "Created directory: ", name

    def read(encryptedName):
        encryptedPath = DCCryptoClient.encryptPath(self.wd)
        keyfileContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedKeyFileName)

    def readFile(name):

        #get encrypted keyfile name
        encryptedKeyFileName = DCCryptoClient.encryptKeyFileName('.kf-' + name, self.passwd)

        #TODO:check that keys exist for all parts of the encrypted path

        encryptedPath = DCCryptoClient.encryptPath(self.wd)

        #request keyfile
        keyfileContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedKeyFileName)

        #construct key object
        keyObj = Key(self.passwd, keyfileContent)

        #save keyobj for later
        DCCryptoClient.addKeyObj('.kf-' + name, keyObj)

        #request encrypted file using encrypted file name
        encryptedFileName = DCCryptoClient.encryptName(name, keyObj)

        encryptedFileContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedFileName)

        #decrypt file contents
        decryptedFileContent = DCCryptoClient.decryptFile(encryptedFileContent, keyObj)

        #verify contents

        return decryptedFileContent

    def readDir(name):

        #get encrypted keyfile name
        encryptedKeyFileName = DCCryptoClient.encryptKeyFileName('.kf-' + name, self.passwd)

        #TODO:check that keys exist for all parts of the encrypted path

        encryptedPath = DCCryptoClient.encryptPath(self.wd)

        #request keyfile
        keyfileContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedKeyFileName)

        #construct key object
        keyObj = Key(self.passwd, keyfileContent)

        #save keyobj for later
        DCCryptoClient.addKeyObj('.kf-' + name, keyObj)

        #request encrypted file using encrypted file name
        encryptedFileName = DCCryptoClient.encryptName(name, keyObj)

        encryptedFileContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedFileName)

        #decrypt file contents
        decryptedFileContent = DCCryptoClient.decryptFile(encryptedFileContent, keyObj)

        #verify contents

        return decryptedFileContent
        '''
        #write decrypted content to new temporary file
        with open('tmp/' + name, 'w') as f:
            f.write(decryptedFileContent)

        return "Created temporary file: " + name + "in location: " + os.getcwd() + "/tmp/" + name
        '''


    def write(name, content):

        #TODO: If file doesn't exist create it
        '''
        #read temprorary contents from temp file
        with open('tmp/' + name, 'r') as content_file:
            content = content_file.read()
        '''

        #get associated key for this file
        if DCCryptoClient.hasKey('.kf-' + name):
            keyfile = DCCryptoClient.getKey('.kf-' + name)
        else:
            #request keyfile
            encryptedKeyFileName = DCCryptoClient.encryptKeyFileName('.kf-' + name, self.passwd)
            encryptedPath = DCCryptoClient.encryptPath(self.wd)
            keyfileContent = self.HttpClient.sendReadCommand(encryptedPath + '/' + encryptedKeyFileName)
            keyfile = Key(self.passwd, keyfileContent)

        #encrypt file's new contents
        encryptedContent = DCCryptoClient.encryptFile(content, keyfile)

        #craft write request to server
        encryptedFileName = DCCryptoClient.encryptName(name, keyfile)
        encryptedPath = DCCryptoClient.encryptPath(self.wd)

        self.HttpClient.sendWriteRequest(encryptedPath + '/' + encryptedFileName,
                                         encryptedContent)

        return name + " written"

    def delete(args):
        name = args[0]

        #------- request to delete key file ----------
        #get encrypted keyfile name
        encryptedKeyFileName = DCCryptoClient.encryptKeyFileName('.kf-' + name, self.passwd)
        encryptedPath = DCCryptoClient.encryptPath(self.wd)

        #request keyfile
        command = {'method': 'read', 
                   'path': encryptPath, 
                   'name': encryptedKeyFileName}
        keyfileContent = self.HttpClient.sendCommand(command)

        #construct key object
        keyObj = Key(self.passwd, keyfileContent)

        #request encrypted file using encrypted file name
        encryptedFileName = DCCryptoClient.encryptName(name, keyObj)

        #---------- request to delete file -----------
        #delete keyfile
        command = {'method': 'delete', 
                   'path': encryptPath, 
                   'name': encryptedKeyFileName}
        self.HttpClient.sendCommand(command)

        #delete file
        command = {'method': 'delete', 
                   'path': encryptPath, 
                   'name': encryptedFileName}
        self.HttpClient.sendCommand(command)

        # -- request to change parent directory structure --
        command = {'method': 'read', 
                   'path': encryptedPath}
        encryptedFileContent = self.HttpClient.sendCommand(command)

        #decrypt file contents
        decryptedFileContent = DCCryptoClient.decryptFile(encryptedFileContent, keyObj)

        #remove file name from directory
        newContent = "" #TODO: MARCEL - clear the line in the directory to send back

        #encrypt file's new contents
        encryptedContent = DCCryptoClient.encryptFile(newContent, keyfile)

        #craft write request to server
        encryptedFileName = DCCryptoClient.encryptName(name, keyfile)
        encryptedPath = DCCryptoClient.encryptPath(self.wd)

        command = {'method': 'write',  
                   'path': encryptedPath,
                   'content': encryptedContent}

        self.HttpClient.sendCommand(command)

        return

    def rename(args):


    def login(args):
        if len(args) != 2:
            raise CommandError("Usage: login username passwd")

        if self.username:
            raise CommandError("Already logged in.")

        self.HttpClient
        self.username = args[0]
        self.passwd = args[1]

    def logout(args):
        if len(args) != 0:
            raise CommandError("Usage: logout")

        if not self.username:
            raise CommandError("Not logged in.")
        self.username = None
        self.passwd = None

    def exit_shell(args):
        if len(args) != 0:
            print "Not a valid command, make sure exit has not arguments"
        sys.exit(0)


    def show_help(args):
        print "Available commands:"
        for cmd in commands:
            print "- " + cmd


    commands = {
        'create': self.createFile,
        'delete': self.delete,
        'read': self.read,
        'write': self.write,
        'rename': self.rename,
        'login': self.login,
        'mkdir': self.mkdir,
        'logout': self.logout,
    }

    def run_command(cmd, args):
        print "Running %s with args %s" % (cmd, args, )
        if cmd in commands:
            try:
                commands[cmd](args)
            except CommandError, e:
                print e.message
        else:
            print "%s: command not found" % (cmd, )

    def run():
        try:
            while True:
                cmd_str = raw_input(prompt)
                args = shlex.split(cmd_str)
                if not args: continue
                cmd = args[0]
                run_command(cmd, args[1:])
        except EOFError:
            print "\nEnded Session"


if __name__ == '__main__':
    client = DarkCloudClient()
    client.run()
