#!/usr/bin/env python

import httplib
import sys
import DarkCloudCryptoLib

class HttpClientLib:
    def __init__():
        pass
    def sendCommand(cmd):
        pass
    def frameRequest(cmd):
        pass
    def sendRequest():
        pass


class CommandError(Exception):
    pass


class DarkCloudClient:
    def __init__():
        self.username = None
        self.passwd = None
        self.wd = None

    def sendFile():
        pass

    def createFile(name):
        name = args

        keyfile = DarkCloudCryptoLib.makeKeyFile(self.username, self.passwd)
        encryptedName = DarkCloudCryptoLib.encryptName(name)
        encryptedPath = DarkCloudCryptoLib.encryptPath(self.wd)

        try:
            command = {'method': 'create', 
                       'path': encryptPath, 
                       'name': encryptedName, 
                       'keyfile': keyfile}
            HttpClientLib.sendCommand(command)

        except Exception, e:
            return "Unable to create file: ", name

        return "Created file: ", name

    def mkdir(args):
        name = args

        keyfile = DarkCloudCryptoLib.makeKeyFile(self.passwd, "." + name)
        encryptedName = DarkCloudCryptoLib.encryptName(name)
        encryptedPath = DarkCloudCryptoLib.encryptPath(self.wd)

        try:
            command = {'method': 'mkdir', 
                       'path': encryptPath, 
                       'name': encryptedName, 
                       'keyfile': keyfile}
            HttpClientLib.sendCommand(command)

        except Exception, e:
            return "Unable to create directory: ", name

        return "Created directory: ", name

    def read(args):
        name = args

        #get encrypted keyfile name
        encryptedKeyName = DarkCloudCryptoLib.encryptName("." + name)
        encryptedPath = DarkCloudCryptoLib.encryptPath(self.wd)

        try:
            command = {'method': 'read', 
                       'path': encryptPath, 
                       'name': encryptedKeyName}
            keyfileContent = HttpClientLib.sendCommand(command)

            keyObj = Key(self.passwd, keyfileContent)
            encryptedName = DarkCloudCryptoLib.encryptName(name, keyObj)



        except Exception, e:
            return "Unable to read file: ", name

        return "Created file: ", name

    def write():
        pass

    def login(args):
        if len(args) != 2:
            raise CommandError("Usage: login username passwd")

        if self.username:
            raise CommandError("Already logged in.")

        HttpClientLib
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
        'create': self.create,
        'delete': self.delete,
        'read': self.read,
        'write': self.write,
        'rename': self.rename,
        'login': self.login,
        'mkdir': self.mkdir
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
