import os, sys, re

class Exec(object):

    def __init__(self):
        pass

    def _runCommand(self,args:list,redirectStdOut:bool=False,redirectErrOut:bool=False,background:bool=False):
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
                    os.write(1,"[&]---------------------------------------------------------------Background Job----[&]\n".encode())
                    bg = os.spawnve(os.P_NOWAIT, program, args, os.environ)
                    os.write(1,f"[&]-------------Background process exit code: {bg}, program={program}, args={args}---[&]\n".encode())

                if redirectStdOut or redirectErrOut:
                    # No standard out banner when appending
                    os.execve(program,args,os.environ)
                else:
                    # Standard out with banner
                    #os.write(1, "std::out> \n".encode())
                    os.execve(program, args, os.environ)  # execute program
            else:
                # Standard Error
                if redirectErrOut:
                    os.write(2,f"{args[0]}: Command does not exist\n".encode())

                os.write(1, "std::err> \n".encode())    # change to standard out
                os.write(1,f"{args[0]}: Command does not exist\n".encode())
        else:
            try:
                os.chdir(args[1])
            except FileNotFoundError:
                os.write(1,"cd: Directory does not exist\n".encode())

    def findCommandAndExecute(self,
                              args: list,
                              redirectStdOut: bool = False,
                              redirectErrOut: bool = False,
                              background: bool = False):
        """
        Command that will be checked against every directory in $PATH variable.
        :param args: whatever is typed into the terminal.
        :param redirectStdOut: redirect flag that indicates redirection.
        :param redirectErrOut: redirect to error.
        :param background: background processes of command.
        :return:
        """
        try:
            self._runCommand(args=args,
                             redirectStdOut=redirectStdOut,
                             redirectErrOut=redirectErrOut,
                             background=background)
        except IndexError:
            os.write(1, f"[*] Provide valid command (Empty String)\n".encode())


    def runPipeCommand(self,command:str):
        """
        Execute Pipe command.
        :param command: command string.
        :return:
        """
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
                if ">" in pipe1:
                    filename = str(pipe1[-1])  # Filename for Redirection
                    pipe1 = pipe1[:pipe1.index(">")]
                    # Redirect to Standard Out
                    os.close(1)  # redirect child's stdout
                    os.open(filename, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
                    os.set_inheritable(1, True)

                elif "<" in pipe1:
                    filename = str(pipe1[-1])
                    pipe1 = pipe1[:pipe1.index("<")]
                    # Redirect to Standard In
                    os.close(0)
                    sys.stdin = open(f"{filename}", "r")
                    stdin_fd = sys.stdin.fileno()
                    os.set_inheritable(stdin_fd, True)

                # redirectStdOut: true because we want no print banner repeating.
                self._runCommand(pipe1,redirectStdOut=True,background=backgroundFlag1)
        else:
            os.close(0)
            os.dup(pr)
            os.set_inheritable(0,True)
            for fd in (pw,pr):
                os.close(fd)
            if ">" in pipe2:
                filename = str(pipe2[-1])  # Filename for Redirection
                pipe2 = pipe2[:pipe2.index(">")]
                # Redirect to Standard Out
                os.close(1)
                os.open(filename, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
                os.set_inheritable(1, True)

                self._runCommand(pipe2,redirectStdOut=True,background=backgroundFlag2)
            elif "<" in pipe2:
                filename = str(pipe2[-1])
                pipe2 = pipe2[:pipe2.index("<")]
                # Redirect to Standard In
                os.close(0)
                sys.stdin = open(f"{filename}", "r")
                stdin_fd = sys.stdin.fileno()
                os.set_inheritable(stdin_fd, True)

            self._runCommand(pipe2,redirectStdOut=False,background=backgroundFlag2)
