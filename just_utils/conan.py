import os
import subprocess
import shutil
from itertools import chain
from pathlib import Path
from termcolor import cprint, colored
from alive_progress import alive_bar
from .clean import clean_build_directory

class Conan:
    def __init__(self, package_name: str, build_type: str, verbose: bool, root: Path = Path.cwd()):
        self.root = root
        self.package_name = package_name
        self.build_type = build_type
        self.verbose = verbose

    def _arg(self, name, value):
        if value is None:
            return None
        return ["-o", f"{self.package_name}/*:{name}={value}"]

    def _build_type_arg(self):
        match self.build_type:
            case "debug":
                return "Debug"
            case "release":
                return "Release"
            case "minsizerel":
                return "MinSizeRel"
            case "relwithdebinfo":
                return "RelWithDebInfo"
            case _:
                raise ValueError(f"Unknown build type: {self.build_type}")
    
    def run(self, command: str, args, fwd_args):
        conan_args = [
            "conan",
            command,
            ".",
            "--build=missing",
            "--build=editable",
            f"--settings=build_type={self._build_type_arg()}",
            *(
                self._arg(name, value)
                for name, value in args.items()
            ),
            *fwd_args
        ]     
        flat_args = list(chain.from_iterable(
            arg if isinstance(arg, list) else [arg]
            for arg in conan_args
        ))
        if not self.verbose:
            flat_args.append("-vwarning")
        if self.verbose:
            cprint(f"running: {' '.join(flat_args)}", "green")
        
        env = os.environ.copy()
        env["CLICOLOR_FORCE"] = "1"
        process = subprocess.Popen(
            flat_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env
        )
        with alive_bar(0, title='Running Conan') as bar:
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                if self.verbose:
                    print(line, end='')
                bar()
        return process.wait()
    
    def clean(self):
        clean_build_directory(self.root)

    def fix_presets(self):
        if os.name != "nt":
            return
        if (self.root / "build" / "generators" / "CMakePresets.json").exists():
            with open(self.root / "build" / "generators" / "CMakePresets.json", "r") as f:
                content = f.read()
            try:
                content = content.replace("v143", "v144", 1)
                with open(self.root / "build" / "generators" / "CMakePresets.json", "w") as f:
                    f.write(content)
            except:
                pass