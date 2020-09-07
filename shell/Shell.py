# Author: Manuel Aguilar

import os, sys, re


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

        os.write(1,"[+]--------------------------------------------[+]\n".encode())
        os.write(1, f"About to fork (pid:{self.pid})\n".encode())

        rc = os.fork()

        if rc < 0:
            os.write(2, f"fork failed, returning {rc}\n".encode())
            sys.exit(1)

        elif rc == 0:  # child
            os.write(1, f"Child: My pid=={os.getpid()}.  Parent's pid={self.pid}\n".encode())
            os.write(1, "--------------------------------------------------\n".encode())

            _findCommand(command)

        else:  # parent (forked ok)
            os.write(1, f"Parent: My pid={self.pid}.  Child's pid={rc}\n".encode())
            childPidCode = os.wait()

            os.write(1, "--------------------------------------------------\n".encode())
            os.write(1, f"Parent: Child {childPidCode[0]} terminated with exit code {childPidCode[1]}\n".encode())


def _findCommand(command:str):
    """
    Command that will be checked against every directory in $PATH variable.
    :param command: whatever is typed into the terminal.
    :return:
    """
    args = command.split(" ")  # COMMAND
    result = [dir for dir in re.split(":",os.environ["PATH"]) if os.path.exists(f"{dir}/{args[0]}")]
    for e in result:
        program = f"{e}/{args[0]}"

        os.write(1, "std::out> ".encode())
        os.execve(program, args, os.environ)  # try to exec program
    else:
        os.write(1, "std::err> ".encode())
        os.write(1,f"{args[0]}: Command does not exist\n".encode())

