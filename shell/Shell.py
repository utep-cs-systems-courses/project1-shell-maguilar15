"""
:author Manuel Aguilar
:lab 1
"""

import os, sys, re


class Shell(object):


    def __init__(self,shellPromptToken:str):
        self.pid = os.getpid()
        self.shellPromptToken = shellPromptToken


    def getPid(self):
        """
        Debugger Statement, making sure you can keep track of the pid.
        :return: pid
        """
        return self.pid


    def run(self):
        """
        Run-time engine for terminal.
        :return: shellPrompt for command.
        """
        shellPrompt = str(input(f"({os.getcwd()}){self.shellPromptToken} "))

        if shellPrompt == "exit":
            print("Exit Shell, bye")
            exit()

        self._executedCommandToStandardOutput(shellPrompt)

        return shellPrompt


    def _executedCommandToStandardOutput(self,command:str):
        """
        Execute command to standard out.
        :param command: command to execute in possible paths.
        :return
        """
        os.write(1,"[+]--------------------------------------------[+]\n".encode())
        os.write(1, f"About to fork (pid:{self.pid})\n".encode())
        rc = os.fork()
        if rc < 0:
            os.write(2, f"fork failed, returning {rc}\n".encode())
            sys.exit(1)
        elif rc == 0:  # child
            os.write(1, f"Child: My pid=={os.getpid()}.  Parent's pid={self.pid}\n".encode())
            os.write(1, "--------------------------------------------------\n".encode())

            # Control Standard In(1) and Standard Out(2)
            args = command.split(" ")                    #TODO: Command Parser

            if ">" in args:
                filename = str(args[len(args)-1])                       # Filename for Redirection
                #os.write(1,f'Filename:  {args[3]}'.encode()) ## DEBUG
                ######################################################
                os.close(1)  # redirect child's stdout
                os.open(filename, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
                os.set_inheritable(1, True)
                ######################################################
                args = [args[e] for e in range(2)]
                self._findCommandAndExecute(args)
            elif ">>" in args:
                os.write(1,f'Command: {args[2]} {args[len(args)-1]}'.encode()) ## Redirection
            elif "2>" in args:
                os.write(1,f"ERROR")
            elif "|" in args:
                pipeCommand = command.split("|",2)
            else:
                self._findCommandAndExecute(args)

        else:  # parent (forked ok)
            os.write(1, f"Parent: My pid={self.pid}.  Child's pid={rc}\n".encode())
            childPidCode = os.wait()
            os.write(1, "--------------------------------------------------\n".encode())
            os.write(1, f"Parent: Child {childPidCode[0]} terminated with exit code {childPidCode[1]}\n".encode())


    def _findCommandAndExecute(self,args:list):
        """
        Command that will be checked against every directory in $PATH variable.
        :param args: whatever is typed into the terminal.
        :return:
        """

        paths = [f"{dir}/{args[0]}" for dir in re.split(":", os.environ["PATH"])]
        result = list(filter(lambda p: os.path.exists(p), paths))

        if "cd" not in args:
            # Execute program
            for program in result:
                os.write(1, "std::out> ".encode())
                os.execve(program, args, os.environ)  # execute program
            else:
                os.write(1, "std::err> ".encode())    # change to standard out?
                os.write(1,f"{args[0]}: Command does not exist\n".encode())
        else:
            os.chdir(args[1])
