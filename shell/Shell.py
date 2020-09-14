"""
:author Manuel Aguilar
:lab 1
"""

import os, sys, re

import fileinput

class Shell(object):


    def __init__(self,shellPromptToken:str):
        self.pid = os.getpid()
        self.shellPromptToken = shellPromptToken

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


    def _executedCommandToStandardOutput(self,command:str,background:bool=False):
        """
        Execute command to standard out.
        :param command: command to execute in possible paths.
        :return
        """
        os.write(1,"[+]--------------------------------------------[+]\n".encode())
        os.write(1, f"About to fork (pid:{self.pid})\n".encode())

        fork = os.fork()

        if fork < 0:
            os.write(2, f"fork failed, returning {fork}\n".encode())
            sys.exit(1)
        elif fork == 0:  # child
            os.write(1, f"Child: My pid=={os.getpid()}.  Parent's pid={self.pid}\n".encode())
            os.write(1, "--------------------------------------------------\n".encode())

            # Control Standard In(0) and Standard Out(1)
            args = command.replace("\n","").split()                    #TODO: Command Parser

            if "|" in args:
                self._runPipeCommand(command)
            elif "&" in args:
                args = args[:args.index("&")]
                self._findCommandAndExecute(args, background=True)
            elif ">" in args or ">>" in args:
                filename = str(args[-1])                       # Filename for Redirection
                args = args[:args.index(">")]
                #os.write(1,f'Filename:  {args[3]}'.encode()) ## DEBUG
                ######################################################
                os.close(1)  # redirect child's stdout
                os.open(filename, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
                os.set_inheritable(1, True)
                ######################################################
                #['cat', 'README.md', '>', 'file.txt']
                self._findCommandAndExecute(args,redirectStdOut=True)
            elif "<" in args:
                filename = str(args[-1])
                first = args[:args.index("<")]
                ############################################
                #os.close(0)
                #new_stdin = os.open(f"{filename}",os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
                #os.set_inheritable(0, True)
                #os.dup2(new_stdin,0)
                ###########################################
                os.close(0)
                sys.stdin = open(f"{filename}", "r")
                stdin_fd = sys.stdin.fileno()
                os.set_inheritable(stdin_fd, True)
                ###########################################
                self._findCommandAndExecute(first)
            elif "2>" in args:
                os.write(2,f"ERROR".encode())
            else:
                self._findCommandAndExecute(args)

        else:  # parent (forked ok)
            os.write(1, f"Parent: My pid={self.pid}.  Child's pid={fork}\n".encode())
            # Logic Bomb ? (Check: continue)
            if not background:
                childPidCode = os.wait()
            os.write(1, "--------------------------------------------------\n".encode())
            os.write(1, f"Parent: Child {childPidCode[0]} terminated with exit code {childPidCode[1]}\n".encode())


    def _findCommandAndExecute(self,args:list, redirectStdOut:bool=False,redirectErrOut:bool=False, background:bool=False):
        """
        Command that will be checked against every directory in $PATH variable.
        :param args: whatever is typed into the terminal.
        :param redirectStdOut: redirect flag that indicates redirection.
        :param redirectErrOut: redirect to error.
        :param background: background processes of command.
        :return:
        """
        paths = [f"{dir}/{args[0]}" for dir in re.split(":", os.environ["PATH"])]
        result = list(filter(lambda p: os.path.exists(p), paths))

        if "cd" not in args:
            # Execute program
            for program in result:
                if background:
                    bg = os.spawnve(os.P_WAIT, program, args, os.environ)
                    os.write(2,f"Background process exit code: {bg}\n".encode())
                if redirectStdOut:
                    # No standard out banner when appending
                    os.execve(program,args,os.environ)

                # Standard Out with banner
                os.write(1, "std::out> ".encode())
                os.execve(program, args, os.environ)  # execute program
            else:
                # Standard Error
                if redirectErrOut:
                    os.write(2,f"{args[0]}: Command does not exist\n".encode())
                ############################
                os.write(1, "std::err> ".encode())    # change to standard out
                os.write(1,f"{args[0]}: Command does not exist\n".encode())
        else:
            try:
                os.chdir(args[1])
            except FileNotFoundError:
                os.write(1,"File Path does not exist.\n".encode())

    def _runPipeCommand(self,command:str):
        pipe = command.replace("\n","").split("|")
        pipe1 = pipe[0].replace("\n","").strip().split()
        pipe2 = pipe[1].replace("\n","").strip().split()

        backgroundFlag1 = "&" in pipe1 if True else False
        backgroundFlag2 = "&" in pipe2 if True else False

        pr, pw = os.pipe()
        for fd in (pr, pw):
            os.set_inheritable(fd, True)

        forkCode = os.fork()

        if forkCode < 0:
            os.write(2,"[-] Fork Failed\n".encode())
            sys.exit(1)
        if forkCode == 0:
            os.close(1)
            os.dup(pw)
            os.set_inheritable(1,True)
            for fd in (pr,pw):
                os.close(fd)
            if ">" not in pipe1:
                self._findCommandAndExecute(pipe1,background=backgroundFlag1)
            else:
                self._findCommandAndExecute(pipe1,redirectStdOut=True,background=backgroundFlag1)
        else:
            os.close(0)
            os.dup(pr)
            os.set_inheritable(0,True)
            for fd in (pw,pr):
                os.close(fd)
            if ">" not in pipe2:
                self._findCommandAndExecute(pipe2,background=backgroundFlag2)
            else:
                self._findCommandAndExecute(pipe2,redirectStdOut=True,background=backgroundFlag2)