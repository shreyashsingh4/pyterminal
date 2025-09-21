from typing import List
from utils import Sandbox
from monitor import ps as ps_cmd, cpu as cpu_cmd, mem as mem_cmd

HELP = """
Commands:
  ls [path]             List files
  cd [path]             Change directory (sandboxed to project root)
  pwd                   Show current directory
  mkdir <path>          Create directory (parents allowed)
  rm [-r] <path>        Remove file; use -r for directory tree
  ps [topN]             Show top processes by CPU
  cpu                   Show CPU summary
  mem                   Show memory summary
  help                  Show this help
  exit / quit           Leave the terminal

AI/NL mode:
  nl <english request>  e.g.  nl create a folder test and then go to test
"""

class Shell:
    def __init__(self, sandbox: Sandbox):
        self.sb = sandbox

    def run(self, argv: List[str]) -> str:
        if not argv:
            return ""
        cmd, *args = argv

        try:
            if cmd == "ls":
                return "\n".join(self.sb.ls(args[0] if args else None))
            elif cmd == "cd":
                path = args[0] if args else None
                return self.sb.cd(path)
            elif cmd == "pwd":
                return self.sb.pwd()
            elif cmd == "mkdir":
                if not args:
                    return "Usage: mkdir <path>"
                return self.sb.mkdir(args[0])
            elif cmd == "rm":
                if not args:
                    return "Usage: rm [-r] <path>"
                recursive = False
                targets = []
                for a in args:
                    if a in ("-r", "--recursive"):
                        recursive = True
                    else:
                        targets.append(a)
                if len(targets) != 1:
                    return "Usage: rm [-r] <path>"
                return self.sb.rm(targets[0], recursive=recursive)
            elif cmd == "ps":
                top = int(args[0]) if args else 10
                return ps_cmd(top)
            elif cmd == "cpu":
                return cpu_cmd()
            elif cmd == "mem":
                return mem_cmd()
            elif cmd in ("help", "?"):
                return HELP.strip()
            elif cmd in ("exit", "quit"):
                raise SystemExit
            else:
                return f"Unknown command: {cmd}\nType 'help' to see available commands."
        except SystemExit:
            raise
        except Exception as e:
            return f"Error: {e}"
