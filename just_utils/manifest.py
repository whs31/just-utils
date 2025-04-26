from pathlib import Path
from termcolor import colored, cprint
import yaml


def _parse(path: Path):
    if not path.exists() or path.is_dir():
        path = path / ".manifest.yml"
        if not path.exists():
            raise ValueError(f"File {path} does not exist")

    yml = yaml.safe_load(path.read_text())
    return yml


class Manifest:
    def __init__(self, path: Path):
        self.path = path
        self._data = _parse(path)
        self.package = self._data.get("package")

    def pretty_print(self):
        cprint(yaml.dump(self._data), "yellow")
