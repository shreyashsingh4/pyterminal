import re

def parse_nl(text: str) -> list[list[str]]:
    """
    Very small, rule-based NL → command translator.
    Examples:
      "create a folder test" -> [["mkdir", "test"]]
      "remove folder build"  -> [["rm", "-r", "build"]]
      "list files"           -> [["ls"]]
      "go to src"            -> [["cd", "src"]]
    Supports simple chaining with 'and then', '&&', ','.
    """
    parts = re.split(r"\band then\b|&&|,|\n", text, flags=re.I)
    cmds: list[list[str]] = []

    for p in parts:
        s = p.strip().lower()
        if not s:
            continue

        
        m = re.search(r"(create|make)\s+(a\s+)?(dir(ectory)?|folder)\s+(.+)", s)
        if m:
            name = m.group(5).strip().strip('"\'')
            cmds.append(["mkdir", name])
            continue

        
        m = re.search(r"(go to|cd to|change dir(ectory)? to)\s+(.+)", s)
        if m:
            cmds.append(["cd", m.group(3).strip().strip('"\'')])
            continue

        
        if re.search(r"list( files)?|show( files)?|ls\b", s):
            cmds.append(["ls"])
            continue

    
        m = re.search(r"(remove|delete|rm)\s+(folder|dir(ectory)?|file)?\s*(.+)?", s)
        if m and m.group(4):
            target = m.group(4).strip().strip('"\'')
            recursive = m.group(2) in {"folder", "dir", "directory"}
            cmds.append(["rm", "-r", target] if recursive else ["rm", target])
            continue

    return cmds
