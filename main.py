import os

from shell.Shell import Shell

if __name__ == "__main__":
    # Environment Variables
    ps1 = os.getenv("PS1")
    customShellPrompt = ps1 if ps1 else "?> " # default shell prompt

    # Start Shell Object
    shell = Shell()

    # FileName
    FILENAME = os.getenv("FILENAME")
    shellOutputFileName = FILENAME if FILENAME else "default-out.txt"

    # Feture Flag?
    quitShell = True

    while quitShell:
        shellPrompt = shell.makeShellPrompt(customShellPrompt)
        if shellPrompt != "exit":
            shell.runCommand(shellPrompt, shellOutputFileName)
        else:
            quitShell = False

    print("Exit Shell, bye")