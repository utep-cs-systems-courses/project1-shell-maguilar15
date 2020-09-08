import os

from shell.Shell import Shell

if __name__ == "__main__":
    # Environment Variables: Shell Prompt Token
    ps1 = os.getenv("PS1")
    customShellPrompt = ps1 if ps1 else "?> " # default shell prompt token

    # Start Shell Object
    shell = Shell()

    while True:
        try:
            shellPrompt = shell.makeShellPrompt(customShellPrompt)

            if shellPrompt == "exit":
                print("Exit Shell, bye")
                exit()
            else:
                shell.runCommand(shellPrompt)

        except KeyboardInterrupt:
            print("\nKeyboard Interrupt <<<Ctrl+C>>>")
            exit()
        except EOFError:
            print("\nKeyboard Interrupt <<<Ctrl+D>>>")
            exit()
