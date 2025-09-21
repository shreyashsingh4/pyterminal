import shlex
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, PathCompleter, WordCompleter
from prompt_toolkit.history import FileHistory

from utils import Sandbox
from shell import Shell
from nl_parser import parse_nl

COMMANDS = ["ls", "cd", "pwd", "mkdir", "rm", "ps", "cpu", "mem", "help", "exit", "quit", "nl"]

class HybridCompleter(Completer):
    def __init__(self, sandbox: Sandbox):
        self.sb = sandbox
        self.words = WordCompleter(COMMANDS)
        self.paths = PathCompleter(only_directories=False, expanduser=True)

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        parts = shlex.split(text) if text.strip() else []
        if len(parts) <= 1:
            # complete command names
            for c in self.words.get_completions(document, complete_event):
                yield c
        else:
            # complete paths
            for c in self.paths.get_completions(document, complete_event):
                yield c

def main():
    root = Path.cwd()  
    sb = Sandbox(root)
    sh = Shell(sb)
    hist_file = Path.home() / ".pyterminal_history"
    session = PromptSession(
        history=FileHistory(str(hist_file)),
        completer=HybridCompleter(sb),
        complete_while_typing=True
    )

    from monitor import banner
    print(banner())
    print("Sandbox root:", root)
    print("Type 'help' for commands. Use 'nl <english>' for natural-language actions.\n")

    while True:
        try:
            prompt = f"[{sb.pwd()}]$ "
            line = session.prompt(prompt)
            if not line.strip():
                continue

            if line.strip().startswith("nl "):
                nl_text = line.strip()[3:]
                plans = parse_nl(nl_text)
                if not plans:
                    print("Could not parse that into commands.")
                    continue
                for p in plans:
                    print(f"# {p!r}")
                    out = sh.run(p)
                    if out:
                        print(out)
                continue

            args = shlex.split(line)
            out = sh.run(args)
            if out:
                print(out)

        except (EOFError, KeyboardInterrupt):
            print("\nExiting…")
            break
        except SystemExit:
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
