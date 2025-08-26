import os
import shutil
import pathlib

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.build import check_min_cppstd
from conan.tools.files import rmdir, copy
from conan.tools.microsoft import is_msvc


class CoronaRecipe(ConanFile):
    name = "corona"
    version = "2.8.12"
    description = "Corona plugin for MMS engine"
    settings = "os", "compiler", "build_type"
    exports_sources = "*"
    options = {
        "test": [True, False],
        "with_rpath": [True, False],
        "with_neural": [True, False],
        "with_vt100": [True, False],
        "with_watermark": [True, False],
    }
    default_options = {
        "test": False,
        "with_rpath": True,
        "with_neural": False,
        "with_vt100": True,
        "with_watermark": False,
    }

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def binary_dir(self):
        return (
            os.path.join(self.build_folder, "bin", str(self.settings.build_type))
            if is_msvc(self)
            else os.path.join(self.build_folder, "bin")
        )

    @property
    def plugins_dir(self):
        return os.path.join(self.binary_dir, "plugins")

    @property
    def plugins_lib_dir(self):
        return os.path.join(self.plugins_dir, "lib")

    @property
    def geoservice_dir(self):
        return os.path.join(self.binary_dir, "geoservices")

    @staticmethod
    def libname(name: str):
        if os.name == "nt":
            return f"{name}.dll"
        return f"lib{name}.so"

    def requirements(self):
        self.requires(
            "mms/2.63.1@radar/dev", options={"qt": 6, "shared_plugins": False}
        )

        self.requires(
            "mms.api/2.63.0@radar/dev", transitive_headers=True, transitive_libs=True
        )
        self.requires(
            "quasar.api/cci.20250430@whs31/dev",
            transitive_headers=True,
            transitive_libs=True,
        )
        self.requires("quasar.protobufs/[=0.1.7]@quasar/dev")
        self.requires(
            "rolly/[>=2.5.0]@radar/dev",
            force=True,
            transitive_headers=True,
            transitive_libs=True,
        )
        self.requires("frozen/1.2.0", transitive_headers=True, transitive_libs=True)
        self.requires("asio/1.32.0", transitive_headers=True, transitive_libs=True)
        self.requires("protobuf/5.27.0")
        self.requires("grpc/1.67.1", override=True)
        self.requires("asio-grpc/2.9.2", options={"backend": "asio"})
        self.requires("imgui/cci.20230105+1.89.2.docking", force=True)
        self.requires("implot/0.16")
        self.requires("taskflow/3.9.0")

        if self.options.with_vt100:
            self.requires("corona.vt100/0.1.9@quasar/dev")

        if self.options.test:
            self.requires("catch2/[=3.7.1]")

    def build_requirements(self):
        # self.tool_requires("rust/system@whs31/stable")
        self.tool_requires("cmake_helpers/[>=0.1.7]@radar/dev")
        self.tool_requires("protobuf/<host_version>")

    def layout(self):
        cmake_layout(self)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def configure(self):
        self.options["quasar.api/*"].shared = False
        self.options["spdlog/*"].shared = True

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["CORONA_TEST"] = self.options.test
        tc.cache_variables["CORONA_WITH_RPATH"] = self.options.with_rpath
        tc.cache_variables["CORONA_WITH_NEURAL"] = self.options.with_neural
        tc.cache_variables["CORONA_WITH_VT100"] = self.options.with_vt100
        tc.cache_variables["CORONA_WITH_WATERMARK"] = self.options.with_watermark
        tc.generate()

        def copy_plugin(name: str):
            copy(
                self,
                "*",
                src=pathlib.Path(self.dependencies[name].cpp_info.resdirs[0])
                    / "plugins",
                dst=self.plugins_dir,
                keep_path=True,
            )
            self.output.info(f"Copied {name} plugin to {self.plugins_dir}")

        def copy_protobufs(name: str, target_dir: str = None):
            if target_dir is None:
                target_dir = name
            target = pathlib.Path(self.build_folder) / target_dir
            resdir = pathlib.Path(self.dependencies[name].cpp_info.resdirs[0]) / "proto"
            self.output.info(f"Copying .proto files from {resdir} into {target}")
            copy(self, "*.proto", src=resdir, dst=target)

        copy_protobufs("quasar.protobufs")
        copy_plugin("mms")
        if self.options.with_vt100:
            copy_plugin("corona.vt100")

        for dep in self.dependencies.values():
            bin_extensions = [".dll", ".dylib", ".so.*", ".so"]
            exclude = [
                "magic_enum",
                "range-v3",
                "frozen",
                "argparse",
                "nlohmann_json",
                "ipaddress",
                "asio",
                "cmake",
                "taskflow",
                "imgui",
                "implot",
                "json-schema-validator",
                "cmake_helpers",
                "corona.vt100",
            ]
            BINARY_DEPENDENCIES = [
                "mms",
                "mms.api",
                "mms.geoservice",
                "rolly",
                "fmt",
                "spdlog",
                "dlm",
            ]
            BINARY_DEPENDENCIES_LIB_EXCLUDE = [
                self.libname("ruler"),
                self.libname("tile_loader"),
                self.libname("time"),
            ]
            for ext in bin_extensions:
                if dep.ref.name in exclude:
                    continue
                try:
                    if dep.ref.name in BINARY_DEPENDENCIES:
                        copy(
                            self,
                            f"*",
                            dep.cpp_info.bindirs[0],
                            self.binary_dir,
                            excludes=BINARY_DEPENDENCIES_LIB_EXCLUDE,
                        )
                        copy(
                            self,
                            f"*{ext}",
                            dep.cpp_info.libdirs[0],
                            self.binary_dir,
                            excludes=BINARY_DEPENDENCIES_LIB_EXCLUDE,
                        )
                        self.output.info(f"copied {dep.ref.name} binaries")
                    else:
                        copy(
                            self,
                            f"*{ext}",
                            dep.cpp_info.bindirs[0],
                            self.plugins_lib_dir,
                        )
                        copy(
                            self,
                            f"*{ext}",
                            dep.cpp_info.libdirs[0],
                            self.plugins_lib_dir,
                        )
                        self.output.info(f"copied {dep.ref.name} binaries")
                except Exception as e:
                    self.output.warning(f"failed to copy {dep.ref.name} binaries: {e}")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "corona")
        self.cpp_info.set_property("cmake_target_name", "quasar::corona")
        self.cpp_info.libs = ["corona"]
