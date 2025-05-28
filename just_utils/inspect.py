import json
import subprocess
from pathlib import Path
from termcolor import colored, cprint


def _inspect(path: Path):
    if not path.exists():
        raise ValueError(f"File {path} does not exist")
    return json.loads(
        subprocess.check_output(
            ["conan", "inspect", str(path), "--format=json"],
            text=True,
            encoding="utf-8",
        )
    )


class ConanFileMetadata:
    def __init__(self, path: Path):
        self.path = path
        self._data = _inspect(path)
        self.name = self._data.get("name")
        self.user = self._data.get("user")
        self.url = self._data.get("url")
        self.license = self._data.get("license")
        self.author = self._data.get("author")
        self.description = self._data.get("description")
        self.homepage = self._data.get("homepage")
        self.build_policy = self._data.get("build_policy")
        self.upload_policy = self._data.get("upload_policy")
        self.revision_mode = self._data.get("revision_mode")
        self.provides = self._data.get("provides")
        self.deprecated = self._data.get("deprecated")
        self.win_bash = self._data.get("win_bash")
        self.win_bash_run = self._data.get("win_bash_run")
        self.default_options = self._data.get("default_options")
        self.options_description = self._data.get("options_description")
        self.version = self._data.get("version")
        self.topics = self._data.get("topics")
        self.package_type = self._data.get("package_type")
        self.languages = self._data.get("languages")
        self.settings = self._data.get("settings")
        self.options = self._data.get("options")
        self.options_definitions = self._data.get("options_definitions")
        self.generators = self._data.get("generators")
        self.requires = self._data.get("requires")
        self.python_requires = self._data.get("python_requires")
        self.source_folder = self._data.get("source_folder")
        self.build_folder = self._data.get("build_folder")
        self.generators_folder = self._data.get("generators_folder")
        self.package_folder = self._data.get("package_folder")
        self.immutable_package_folder = self._data.get("immutable_package_folder")
        self.label = self._data.get("label")
        self.vendor = self._data.get("vendor")

    @property
    def is_lts(self):
        return "+lts" in self.version

    @property
    def is_beta(self):
        return "+beta" in self.version

    @property
    def is_rc(self):
        return "+rc" in self.version

    @property
    def is_dev(self):
        return "+dev" in self.version

    @property
    def preferred_channel(self):
        if self.is_lts:
            return "stable"
        return "dev"

    def pretty_print(self, verbose=True):
        if not verbose:
            return
        print("-- conanfile --")
        print(f"name:                {colored(self.name, 'magenta', attrs=['bold'])}")
        print(f"user:                {colored(self.user, 'green')}")
        print(f"url:                 {colored(self.url, 'green')}")
        print(f"license:             {colored(self.license, 'magenta')}")
        print(f"author:              {colored(self.author, 'magenta')}")
        print(
            f"description:         {colored(self.description, 'magenta', attrs=['bold'])}"
        )
        print(f"homepage:            {colored(self.homepage, 'green')}")
        print(f"build_policy:        {colored(self.build_policy, 'green')}")
        print(f"upload_policy:       {colored(self.upload_policy, 'green')}")
        print(f"revision_mode:       {colored(self.revision_mode, 'green')}")
        print(f"provides:            {colored(self.provides, 'green')}")
        print(f"deprecated:          {colored(self.deprecated, 'green')}")
        print(f"win_bash:            {colored(self.win_bash, 'green')}")
        print(f"win_bash_run:        {colored(self.win_bash_run, 'green')}")
        print(f"version:             {colored(self.version, 'yellow', attrs=['bold'])}")
        print(f"topics:              {colored(self.topics, 'green')}")
        print(f"package_type:        {colored(self.package_type, 'green')}")
        print(f"languages:           {colored(self.languages, 'green')}")
        print(f"settings:            {colored(self.settings, 'green')}")
        print(f"options:             {colored(self.options, 'green')}")
        print(f"options_definitions: {colored(self.options_definitions, 'green')}")
        print(f"generators:          {colored(self.generators, 'green')}")
        print(f"requires:            {colored(self.requires, 'green')}")
        print(f"python_requires:     {colored(self.python_requires, 'green')}")
        print(f"source_folder:       {colored(self.source_folder, 'green')}")
        print(f"build_folder:        {colored(self.build_folder, 'green')}")
        print(f"generators_folder:   {colored(self.generators_folder, 'green')}")
        print(f"package_folder:      {colored(self.package_folder, 'green')}")
        print(f"immutable_pf:        {colored(self.immutable_package_folder, 'green')}")
        print(f"label:               {colored(self.label, 'green')}")
        print(f"vendor:              {colored(self.vendor, 'green')}")

        print()
        print(f"is_lts:              {colored(self.is_lts, 'yellow')}")
        print(f"is_beta:             {colored(self.is_beta, 'yellow')}")
        print(f"is_rc:               {colored(self.is_rc, 'yellow')}")
        print(f"is_dev:              {colored(self.is_dev, 'yellow')}")
        print(f"preferred_channel:   {colored(self.preferred_channel, 'yellow')}")
        print()
