# Global Imports
import os

# Local Imports
from shell.Shell import Shell

if __name__ == "__main__":
    # Environment Variables: Shell Prompt Token
    ps1 = os.getenv("PS1")
    color = os.getenv("COLOR","0")

    customShellPrompt = ps1 if ps1 else "?> "   # default shell prompt token
    colorShellPrompt = int(color) if 1 else 0   # default no color on shell

    # Initialize Shell
    shell = Shell(customShellPrompt,colorShellPrompt)

    while True:
        try:

            shell.run()

        except KeyboardInterrupt:
            os.write(1,"\nKeyboard Interrupt <<<Ctrl+C>>>\n".encode())
            exit()
        except EOFError:
            os.write(1,"\nKeyboard Interrupt <<<Ctrl+D>>>\n".encode())
            exit()
