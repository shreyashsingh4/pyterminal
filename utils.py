from pathlib import Path

class Sandbox:
    """
    Prevents 'cd ..' escaping above the project root. Resolves any input path
    to an absolute path contained within the sandbox root.
    """
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.cwd = self.root

    def _resolve_inside(self, p: Path) -> Path:
        target = (self.cwd / p).resolve() if not p.is_absolute() else p.resolve()
        try:
            target.relative_to(self.root)
        except ValueError:
            raise PermissionError("Path escapes sandbox root")
        return target

    def ls(self, path: str | None = None) -> list[str]:
        target = self.cwd if path is None else self._resolve_inside(Path(path))
        if not target.exists():
            raise FileNotFoundError(f"No such file or directory: {target}")
        if target.is_file():
            return [target.name]
        return sorted([p.name + ("/" if p.is_dir() else "") for p in target.iterdir()])

    def cd(self, path: str | None = None) -> str:
        if path in (None, "", "~"):
            self.cwd = self.root
            return str(self.cwd)
        target = self._resolve_inside(Path(path))
        if not target.exists() or not target.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        self.cwd = target
        return str(self.cwd)

    def pwd(self) -> str:
        return str(self.cwd)

    def mkdir(self, path: str) -> str:
        target = self._resolve_inside(Path(path))
        target.mkdir(parents=True, exist_ok=False)
        return f"Directory created: {target.name}"

    def rm(self, path: str, recursive: bool = False) -> str:
        target = self._resolve_inside(Path(path))
        if not target.exists():
            raise FileNotFoundError(f"No such file or directory: {path}")
        if target.is_file():
            target.unlink(missing_ok=False)
            return f"Removed file: {target.name}"
        
        if recursive:
            import shutil
            shutil.rmtree(target)
            return f"Removed directory tree: {target.name}"
        else:
            target.rmdir()  
            return f"Removed directory: {target.name}"
