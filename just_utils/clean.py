import os 
import shutil
from termcolor import cprint
from pathlib import Path

def clean_build_directory(root: Path = Path.cwd()):
    build_dir = root / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        cprint(f"removed {build_dir}", "yellow")
    target_dir = root / "target"
    if target_dir.exists():
        shutil.rmtree(target_dir)
        cprint(f"removed {target_dir}", "yellow")
    cmake_presets = root / "CMakeUserPresets.json"
    if cmake_presets.exists():
        os.remove(cmake_presets)
        cprint(f"removed {cmake_presets}", "yellow")