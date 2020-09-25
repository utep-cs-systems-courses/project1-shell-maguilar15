#! /usr/bin/env python3

"""
:author Manuel Aguilar
:lab 1
"""

import os, sys

from .Color import Color
from .Exec import Exec as ExecuteCommand

class Shell(object):


    def __init__(self,shellPromptToken:str,shellColor:int=0):
        self.pid = os.getpid()
        self.shellPromptToken = shellPromptToken
        self.shellColor = shellColor
        self.cmd = ExecuteCommand()


    def _makeShell(self):
        """
        Make Shell With Color.
        :return: shellPrompt
        """
        if self.shellColor:
            shellBanner = Color.F_LightMagenta + f"({os.getcwd()}){self.shellPromptToken} " + Color.F_LightYellow
        else:
            shellBanner = f"({os.getcwd()}){self.shellPromptToken} "

        os.write(1, shellBanner.encode())
        shellPrompt = os.read(0,128).decode()

        return shellPrompt


    def run(self):
        """
        Run-time engine for terminal.
        :return: shellPrompt for command.
        """
        shellPrompt = self._makeShell()

        if shellPrompt == "exit":
            print("Exit Shell, bye")
            exit()

        if not shellPrompt:
            pass
        else:
            self.executedCommandToStandardOutput(shellPrompt)

        return shellPrompt


    def executedCommandToStandardOutput(self,command:str):
        """
        Execute command to standard out.
        :param command: command to execute in possible paths.
        :return
        """
        # Background Flag
        backgroundFlag = "&" in command if True else False
        pid = self.pid

        os.write(1, "[+]--------------------------------------------[+]\n".encode())
        os.write(1, f"About to fork (pid:{pid})\n".encode())

        fork = os.fork()

        if fork < 0:
            os.write(2, f"fork failed, returning {fork}\n".encode())
            sys.exit(1)
        elif fork == 0:  # child
            os.write(1, f"Child: My pid=={os.getpid()}.  Parent's pid={pid}\n".encode())
            os.write(1, "--------------------------------------------------\n".encode())

            # Control Standard In(0) and Standard Out(1)
            args = command.replace("&", "").replace("\n", "").split()

            if "|" in args:
                self.cmd.runPipeCommand(command)
            elif ">" in args or ">>" in args:
                filename = str(args[-1])  # Filename for Redirection
                args = args[:args.index(">")]
                # Standard Out
                os.close(1)  # redirect child's stdout
                os.open(filename, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
                os.set_inheritable(1, True)

                self.cmd.findCommandAndExecute(args=args, redirectStdOut=True, background=backgroundFlag)
            elif "<" in args:
                filename = str(args[-1])
                args = args[:args.index("<")]
                # Standard In
                os.close(0)
                sys.stdin = open(f"{filename}", "r")
                stdin_fd = sys.stdin.fileno()
                os.set_inheritable(stdin_fd, True)

                self.cmd.findCommandAndExecute(args=args, background=backgroundFlag)
            elif "2>" in args:
                filename = str(args[-1])
                args = args[:args.index("2>")]
                # Standard Error
                os.close(2)
                sys.stdin = open(f"{filename}", "r")
                stdin_fd = sys.stdin.fileno()
                os.set_inheritable(stdin_fd, True)

                self.cmd.findCommandAndExecute(args=args, redirectErrOut=True, background=backgroundFlag)
            else:
                self.cmd.findCommandAndExecute(args=args, background=backgroundFlag)

        else:  # parent (forked ok)
            os.write(1, f"Parent: My pid={pid}.  Child's pid={fork}\n".encode())

            # Background
            if backgroundFlag:
                pass

            childPidCode = os.wait()

            os.write(1, "--------------------------------------------------\n".encode())
            os.write(1, f"Parent: Child {childPidCode[0]} terminated with exit code {childPidCode[1]}\n".encode())