import os

from shell.Shell import Shell

if __name__ == "__main__":
    # Environment Variables
    # Shell Prompt Token
    ps1 = os.getenv("PS1")
    customShellPrompt = ps1 if ps1 else "?> " # default shell prompt token
    # FileName
    FILENAME = os.getenv("FILENAME")
    shellOutputFileName = FILENAME if FILENAME else "default-out.txt"

    # Start Shell Object
    shell = Shell()

    # Feature Flag?
    quitShell = True

    while True:
        shellPrompt = shell.makeShellPrompt(customShellPrompt)
        if shellPrompt == "exit":
            print("Exit Shell, bye")
            exit()
        else:
            shell.runCommand(shellPrompt)
