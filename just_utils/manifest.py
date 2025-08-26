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
    def __init__(self, path: Path = Path.cwd() / ".manifest.yml"):
        self.path = path
        self._data = _parse(path)
        self.package = self._data.get("package")

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def pretty_print(self, verbose=True):
        if not verbose:
            return
        print("-- manifest --")
        cprint(yaml.dump(self._data), "yellow")
        print()
