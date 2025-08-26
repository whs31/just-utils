import os
import sys
import re
import yaml
import semver
from pathlib import Path
from termcolor import cprint, colored
from .manifest import Manifest


MACRO_LINE_TEMPLATE = '#define {}_VERSION_{} {}'
MACRO_LINE_REGEX = r'#\s*define\s+{}_VERSION_{}\s+(\d+)'
CONAN_LINE_TEMPLATE = 'version = "{}"'
CONAN_LINE_REGEX = r'version\s*=\s*"([^"]+)"'
CMAKE_LINE_TEMPLATE = r'\1VERSION {}\3'
CMAKE_LINE_REGEX = r'(?m)^(\s*)VERSION\s+(\d+\.\d+\.\d+)(.*)$'


def _read_plugin_metadata(path: Path) -> semver.Version | None:
    try:
        yml = yaml.safe_load(path.read_text())
        return semver.Version.parse(yml['version'])
    except Exception as e:
        cprint(f"Failed to read {path.name}: {e}", "red")
        return None
    
def _write_plugin_metadata(path: Path, version: semver.Version):
    try:
        cprint(f"- Patching {colored(path.name, 'yellow', attrs=['bold'])} with version {colored(version, 'yellow', attrs=['bold'])}", "yellow")
        yml = yaml.safe_load(path.read_text())
        yml['version'] = str(version)
        path.write_text(yaml.dump(yml, allow_unicode=True, sort_keys=False, explicit_start=True))
    except Exception as e:
        cprint(f"Failed to write {path.name}: {e}", "red")

def __extract_define(line: str, prefix: str, suffix: str) -> int | None:
    res = re.search(MACRO_LINE_REGEX.format(prefix, suffix), line)
    if res is None:
        return None
    return res.group(1)

def _read_version_header(path: Path, macro_prefix: str) -> semver.Version | None:
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            major = None
            minor = None
            patch = None
            for line in lines:
                major = __extract_define(line, macro_prefix, suffix="MAJOR") if major is None else major
                minor = __extract_define(line, macro_prefix, suffix="MINOR") if minor is None else minor
                patch = __extract_define(line, macro_prefix, suffix="PATCH") if patch is None else patch
            if major is not None and minor is not None and patch is not None:
                return semver.VersionInfo(major, minor, patch)
            
    except Exception as e:
        cprint(f"Failed to read {path.name}: {e}", "red")
        return None

def _write_version_header(path: Path, macro_prefix: str, version: semver.Version):
    try:
        cprint(f"- Patching {colored(path.name, 'yellow', attrs=['bold'])} with version {colored(version, 'yellow', attrs=['bold'])}", "yellow")
        with open(path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                lines[i] = re.sub(MACRO_LINE_REGEX.format(macro_prefix, "MAJOR"), MACRO_LINE_TEMPLATE.format(macro_prefix, "MAJOR", version.major) , lines[i])
                lines[i] = re.sub(MACRO_LINE_REGEX.format(macro_prefix, "MINOR"), MACRO_LINE_TEMPLATE.format(macro_prefix, "MINOR", version.minor), lines[i])
                lines[i] = re.sub(MACRO_LINE_REGEX.format(macro_prefix, "PATCH"), MACRO_LINE_TEMPLATE.format(macro_prefix, "PATCH", version.patch), lines[i])
            with open(path, 'w') as f:
                f.write(''.join(lines))
    except Exception as e:
        cprint(f"Failed to write {path.name}: {e}", "red")

def _read_line_generic(path: Path, line_regex: str, group: int = 1) -> semver.Version | None:
    try:
        text = path.read_text()
        res = re.search(line_regex, text)
        if res is None:
            return None
        return semver.Version.parse(res.group(group))
    except Exception as e:
        cprint(f"Failed to read {path.name}: {e}", "red")
        return None
    
def _write_line_generic(path: Path, version: semver.Version, line_regex: str, line_template: str):
    try:
        cprint(f"- Patching {colored(path.name, 'yellow', attrs=['bold'])} with version {colored(version, 'yellow', attrs=['bold'])}", "yellow")
        text = path.read_text()
        new_text = re.sub(
            line_regex,
            line_template.format(str(version)),
            text,
            count=1
        )
        path.write_text(new_text)
    except Exception as e:
        cprint(f"Failed to write {path.name}: {e}", "red")

def _read_conan(path: Path) -> semver.Version | None:
    return _read_line_generic(path, CONAN_LINE_REGEX)

def _write_conan(path: Path, version: semver.Version):
    _write_line_generic(path, version, CONAN_LINE_REGEX, CONAN_LINE_TEMPLATE)

def _read_cmake(path: Path) -> semver.Version | None:
    return _read_line_generic(path, CMAKE_LINE_REGEX, group=2)

def _write_cmake(path: Path, version: semver.Version):
    _write_line_generic(path, version, CMAKE_LINE_REGEX, CMAKE_LINE_TEMPLATE)

    
def _print_version(cell_name: str, version: semver.Version | None):
    print(f"- {cell_name:.<25}{colored(version, 'yellow' if version is not None else 'red', attrs=['bold'])}")

def show_version(root: Path = Path.cwd()):
    manifest = Manifest(root / ".manifest.yml")

    
    _print_version("conanfile.py", _read_conan(root / "conanfile.py"))
    _print_version("CMakeLists.txt", _read_cmake(root / "CMakeLists.txt"))

    if 'version' not in manifest:
        return

    if 'header' in manifest['version'] and 'macro_prefix' in manifest['version']['header'] and 'path' in manifest['version']['header']:
        version_header_path = root / manifest['version']['header']['path']
        _print_version(version_header_path.name, _read_version_header(version_header_path, manifest['version']['header']['macro_prefix']))
    if 'plugin_meta' in manifest['version'] and 'path' in manifest['version']['plugin_meta']:
        plugin_meta_path = root / manifest['version']['plugin_meta']['path']
        _print_version(plugin_meta_path.name, _read_plugin_metadata(plugin_meta_path))


def patch_version(version: semver.Version, root: Path = Path.cwd()):
    manifest = Manifest(root / ".manifest.yml")

    if version is None:
        return
    _write_conan(root / "conanfile.py", version)
    _write_cmake(root / "CMakeLists.txt", version)

    if 'version' not in manifest:
        return

    if 'header' in manifest['version'] and 'macro_prefix' in manifest['version']['header'] and 'path' in manifest['version']['header']:
        _write_version_header(root / manifest['version']['header']['path'], manifest['version']['header']['macro_prefix'], version)
    if 'plugin_meta' in manifest['version'] and 'path' in manifest['version']['plugin_meta']:
        _write_plugin_metadata(root / manifest['version']['plugin_meta']['path'], version)

def versions(root: Path = Path.cwd(), patch: bool = False):
    manifest = Manifest(root / ".manifest.yml")

    res = [_read_conan(root / "conanfile.py"), _read_cmake(root / "CMakeLists.txt")]

    if 'version' not in manifest:
        return res

    if 'header' in manifest['version'] and 'macro_prefix' in manifest['version']['header'] and 'path' in manifest['version']['header']:
        version_header_path = root / manifest['version']['header']['path']
        res.append(_read_version_header(version_header_path, manifest['version']['header']['macro_prefix']))
    if 'plugin_meta' in manifest['version'] and 'path' in manifest['version']['plugin_meta']:
        plugin_meta_path = root / manifest['version']['plugin_meta']['path']
        res.append(_read_plugin_metadata(plugin_meta_path))

    # if res is not homogeneous, patch with the lowest version
    if patch and len(set(res)) > 1:
        patch_version(min(res), root)
        return versions(root, patch=False)

    return res

def bump_version_major(root: Path = Path.cwd()):
    ver = min(versions(root))
    patch_version(ver.bump_major(), root)

def bump_version_minor(root: Path = Path.cwd()):
    ver = min(versions(root))
    patch_version(ver.bump_minor(), root)

def bump_version_patch(root: Path = Path.cwd()):
    ver = min(versions(root))
    patch_version(ver.bump_patch(), root)

