# Author: Manuel Aguilar

import os, sys, time, re


class Shell(object):


    def __init__(self):
        self.pid = None
        self.shellPrompt = None


    def makeShellPrompt(self,shellPromptToken:str):
        self.shellPrompt = shellPromptToken
        if shellPromptToken is None:
            shellPrompt = str(input("?> "))  # default
        else:
            shellPrompt = str(input(f"{shellPromptToken} "))

        return shellPrompt

    def getPid(self):
        """
        Debugger Statement, making sure you can keep track of the pid.
        :return: pid
        """
        return self.pid


    def runCommand(self,command:str):
        self.pid = os.getpid()

        os.write(1, ("About to fork (pid:%d)\n" % self.pid).encode())

        rc = os.fork()

        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0:  # child
            os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" %
                         (os.getpid(), self.pid)).encode())
            args = command.split(" ")  # COMMAND
            for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                #os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())  PRINTS TO STDOUT
                try:
                    os.execve(program, args, os.environ)  # try to exec program
                except FileNotFoundError:  # ...expected
                    pass  # ...fail quietly

            os.write(2, ("%s: command does not exist\n" % args[0]).encode())
            sys.exit(1)  # terminate with error

        else:  # parent (forked ok)
            os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" %
                         (self.pid, rc)).encode())
            childPidCode = os.wait()
            os.write(1, ("Parent: Child %d terminated with exit code %d\n" %
                         childPidCode).encode())
