# PyTerminal (Sandboxed)

A safe, sandboxed command terminal implemented in Python.

## Features
- `ls, cd, pwd, mkdir, rm [-r]` with robust errors
- Sandboxed: cannot navigate above project root
- `ps`, `cpu`, `mem` via `psutil`
- History + autocomplete (prompt_toolkit)
- Natural-language helper: `nl <your request>`

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python cli.py
