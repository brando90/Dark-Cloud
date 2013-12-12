import os
import getpass
import DarkCloudClient
import subprocess

prompt = "DarkCloud >>> "

class CommandError(Exception):
    pass

class DCClientParser:
    """docstring for DarkCloudClientParser"""
    def __init__(self, arg):
        self.arg = arg
        self.loggedIn = False
        self.dcClient = None
        self.username = None
        self.passwd = None
        
    def create(args):
        if len(args) == 1:
            name = args[0] #input sanitization
            content = ""
        elif len(args) == 2:
            name = args[0]
            content = args[1]
        else:
            print "Incorrect number of arguments\nUsage: create name [content]"
            return

        #self.dcClient.createFile(name, content)
        print "create ", name, content

        print "Created file: ", name

    def delete(args):
        if len(args) == 1:
            print "Incorrect number of arguments\nUsage: delete name"
            return
        name = args[0]

        #self.dcClient.delete(name)
        print "delete ", name
        print "Deleted file: ", name

    def read(args):
        if len(args) != 1:
            print "Incorrect number of arguments\nUsage: read name"
            return
        name = args[0]

        print "Reading file: " + name + " ..."
        #content = self.dcClient.read(name)
        content = "test"
        with open('tmp/' + name, 'w') as fd:
            return fd.write(content)

    def write(args):
        if len(args) != 1:
            print "Incorrect number of arguments\nUsage: write filename"
            return
        name = args[0]
        with open('tmp/' + name, 'r') as fd:
            content = fd.read()
            #self.dcClient.write(name, content)
            print "write name -> ", content

    def rename(args):
        if len(args) != 2:
            print "Incorrect number of arguments\nUsage: read filename"
            return
        name = args[0]
        newName = args[1]
        #self.dcClient.rename(name, newName)
        print "rename", name, newName

    def mkdir(args):
        if len(args) != 1:
            print "Incorrect number of arguments\nUsage: read filename"
            return
        name = args[0]
        #self.dcClient.mkdir(name)
        print "mkdir", name

    def rmdir(args):
        if len(args) != 1:
            print "Incorrect number of arguments\nUsage: read filename"
            return
        name = args[0]
        #self.dcClient.rmdir(name)
        print "rmdir", name

    def ls():
        pass

    def cd(args):
        if len(args) != 1:
            print "Incorrect number of arguments\nUsage: read filename"
            return
        name = args[0]
        if name == '..':
            self.dcClient.wd.up(1)
        else:
            self.dcClient.wd.down(name)

    def vim(args):
        if len(args) != 1:
            print "Incorrect number of arguments\nUsage: read filename"
            return
        name = args[0]
        print "Openning vim"
        subprocess.call('vim tmp/' + name, shell=True)
        print "Completed"

    def showReadFiles():
        os.listdir('tmp')

    def login():
        self.username = raw_input('Username: ')
        self.passwd = getpass.getpass()

        #sanitize input?

        self.dcClient = DCClient(self.username, self.passwd)
        self.loggedIn = True
        prompt = "DarkCloud:" + self.username + " >>> "

    def logout(args):
        if len(args) != 0:
            raise CommandError("Usage: logout")

        self.username = None
        self.passwd = None
        self.dcClient = None
        prompt = "DarkCloud >>> "

    def exit_shell(args):
        if len(args) != 0:
            print "Not a valid command, make sure exit has not arguments"
        if raw_input('Warning: unwritten files in local directory will be deleted! Do you wish to continue? [y/N]') == 'y':
            sys.exit(0)


    def show_help(args):
        print "Available commands:"
        for cmd in commands:
            print "- " + cmd


    commands = {
        'create': self.create,
        'touch': self.create,
        'delete': self.delete,
        'rm': self.delete,
        'read': self.read,
        'write': self.write,
        'rename': self.rename,
        'login': self.login,
        'logout':self.logout,
        'mkdir': self.mkdir,
        'rmdir': self.rmdir,
        'ls': self.ls,
        'logout': self.logout,
        'exit': self.exit_shell,
        'help': self.show_help,
        'cd': self.cd,
        'vim': self.vim,
        'readFiles': self.showReadFiles #maybe
    }

    def run_command(cmd, args):
        print "Running %s with args %s" % (cmd, args, )
        if cmd in commands:
            if not self.loggedIn and cmd != 'login':
                print "Please login before executing commands."
            try:
                commands[cmd](args)
            except CommandError, e:
                print e.message
        else:
            print "%s: command not found" % (cmd, )

# *** Run Dark Cloud Client ***

def run():
    client = DarkCloudClientParser()
    os.mkdir('tmp')
    try:
        while True:
            cmd_str = raw_input(prompt)
            args = shlex.split(cmd_str)
            if not args: continue
            cmd = args[0]
            client.run_command(cmd, args[1:])
    except EOFError:
        print "\nEnded Session"
    subprocess.call('touch foo', shell=True)


if __name__ == '__main__':
    run()