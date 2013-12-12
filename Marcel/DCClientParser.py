import os
import getpass
import DarkCloudClient
import subprocess
import shlex
import sys
import re

prompt = "DarkCloud >>> "

class CommandError(Exception):
    pass

def isUnsanitizedName(name):
    return re.match("\..*|\.kc-.*|\.ls-.*", name):

class DCClientParser:
    """docstring for DarkCloudClientParser"""
    def __init__(self):
        self.loggedIn = False
        self.dcClient = None
        self.username = None
        self.passwd = None
        self.commands = {
            'create': self.create,
            'touch': self.create,
            'delete': self.delete,
            'rm': self.delete,
            'read': self.read,
            'write': self.write,
            'rename': self.rename,
            'login': self.login,
            'logout': self.logout,
            'mkdir': self.mkdir,
            'rmdir': self.rmdir,
            'ls': self.ls,
            'exit': self.exit_shell,
            'help': self.show_help,
            'cd': self.cd,
            'vim': self.vim,
            'newAccount': newAccount,
            'readFiles': self.showReadFiles #maybe
        }
        
    def newAccount(self, args):
        un = raw_input('Username: ')
        pd = getpass.getpass()

        if isUnsanitizedName(un):
            print "Invalid username, please select a different username."
            return
        self.username = un
        self.passwd = pd

        #sanitize input?

        self.dcClient = DarkCloudClient.createAccount(self.username, self.passwd)

    def create(self, args):
        if len(args) == 2:
            name = args[1] #input sanitization
            content = ""
        elif len(args) == 3:
            name = args[1]
            content = args[2]
        else:
            print "Incorrect number of arguments\nUsage: create name [content]"
            return

        if isUnsanitizedName(name):
            print "Invalid file name."
            return

        #self.dcClient.createFile(name, content)
        print "create ", name, content

        print "Created file: ", name

    def delete(self, args):
        if len(args) != 2:
            print "Incorrect number of arguments\nUsage: delete name"
            return
        name = args[1]

        if isUnsanitizedName(name):
            print "Invalid file name."
            return

        #self.dcClient.delete(name)
        print "delete ", name
        print "Deleted file: ", name

    def read(self, args):
        if len(args) != 2:
            print "Incorrect number of arguments\nUsage: read name"
            return
        name = args[1]
        if isUnsanitizedName(name):
            print "Invalid file name."
            return

        print "Reading file: " + name + " ..."
        #content = self.dcClient.read(name)
        content = "test"
        with open('tmp/' + name, 'w') as fd:
            return fd.write(content)

    def write(self, args):
        if len(args) != 2:
            print "Incorrect number of arguments\nUsage: write filename"
            return
        name = args[1]
        if isUnsanitizedName(name):
            print "Invalid file name."
            return
        with open('tmp/' + name, 'r') as fd:
            content = fd.read()
            #self.dcClient.write(name, content)
            print "write name -> ", content

    def rename(self, args):
        if len(args) != 3:
            print "Incorrect number of arguments\nUsage: read filename"
            return
        name = args[1]
        newName = args[2]
        if isUnsanitizedName(name) or isUnsanitizedName(newName):
            print "Invalid file name."
            return
        #self.dcClient.rename(name, newName)
        print "rename", name, newName

    def mkdir(self, args):
        if len(args) != 2:
            print "Incorrect number of arguments\nUsage: read filename"
            return
        name = args[1]
        if isUnsanitizedName(name):
            print "Invalid file name."
            return
        #self.dcClient.mkdir(name)
        print "mkdir", name

    def rmdir(self, args):
        if len(args) != 2:
            print "Incorrect number of arguments\nUsage: read filename"
            return
        name = args[1]
        if isUnsanitizedName(name):
            print "Invalid file name."
            return
        #self.dcClient.rmdir(name)
        print "rmdir", name

    def ls(self, args):
        pass

    def cd(self, args):
        if len(args) != 2:
            print "Incorrect number of arguments\nChange directory."
            return
        name = args[1]
        if isUnsanitizedName(name):
            print "Invalid file name."
            return
        if name == '..':
            self.dcClient.wd.up(1)
        else:
            self.dcClient.wd.down(name)

    def vim(self, args):
        if len(args) != 2:
            print "Incorrect number of arguments\nUsage: read filename"
            return
        name = args[1]
        print "Openning vim"
        subprocess.call('vim tmp/' + name, shell=True)
        print "Completed"

    def showReadFiles(self, args):
        print os.listdir('tmp')

    def login(self, args):
        self.username = raw_input('Username: ')
        self.passwd = getpass.getpass()

        if isUnsanitizedName(name):
            print "Invalid file name."
            return

        #self.dcClient = DCClient(self.username, self.passwd)
        self.loggedIn = True
        prompt = "DarkCloud:" + self.username + " >>> "

    def logout(self, args):
        if len(args) != 1:
            raise CommandError("Usage: logout")

        self.username = None
        self.passwd = None
        self.dcClient = None
        prompt = "DarkCloud >>> "

    def exit_shell(self, args):
        if len(args) != 1:
            print "Not a valid command, make sure exit has not arguments"
        if raw_input('Warning: unwritten files in local directory will be deleted! Do you wish to continue? [y/N]') == 'y':
            sys.exit(0)


    def show_help(self, args):
        print "Available commands:"
        for cmd in self.commands:
            print "- " + cmd

    def run_command(self, cmd, args):
        print "Running %s with args %s" % (cmd, args, )
        if cmd in self.commands:
            if not self.loggedIn and cmd != 'login':
                print "Please login before executing commands."
            try:
                self.commands[cmd](args)
            except CommandError, e:
                print e.message
        else:
            print "%s: command not found" % (cmd, )

# *** Run Dark Cloud Client ***

def run():
    parser = DCClientParser()
    if not os.path.exists("tmp"):
        os.mkdir('tmp')
    try:
        while True:
            cmd_str = raw_input(prompt)
            args = shlex.split(cmd_str)
            if not args: continue
            cmd = args[0]
            parser.run_command(cmd, args)
    except EOFError:
        print "\nEnded Session"
    subprocess.call('touch foo', shell=True)


if __name__ == '__main__':
    run()