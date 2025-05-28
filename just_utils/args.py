import argparse
from termcolor import colored


def print_arg(name, value, color="yellow"):
    arg = colored(f"{value}", color, attrs=["bold"])
    print(f"{name:<25}: {arg:<25}")


def default_cmake_parser(additional_choosers=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="verbose mode", default=False
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="clean build directory",
        default=False,
    )
    parser.add_argument(
        "-C",
        "--configure",
        action="store_true",
        help="reconfigure cmake only (no build)",
        default=False,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-b",
        "--build",
        choices=["debug", "release", "minsizerel", "relwithdebinfo"],
        help="choose build mode (debug, release, minsizerel, relwithdebinfo)",
    )
    group.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const="debug",
        dest="build",
        help="enable debug mode",
    )
    group.add_argument(
        "-r",
        "--release",
        action="store_const",
        const="release",
        dest="build",
        help="enable release mode",
    )
    group.add_argument(
        "-m",
        "--minsizerel",
        action="store_const",
        const="minsizerel",
        dest="build",
        help="enable msr mode",
    )
    group.add_argument(
        "-w",
        "--relwithdebinfo",
        action="store_const",
        const="relwithdebinfo",
        dest="build",
        help="enable rwdi mode",
    )

    if "qt" in additional_choosers:
        parser.add_argument(
            "-q",
            "--qt",
            choices=["5", "6"],
            default="5",
            help="Choose Qt version (5, 6)",
        )
    if "shared" in additional_choosers:
        parser.add_argument(
            "-s",
            "--shared",
            action="store_true",
            default=True,
        )
        parser.add_argument("-a", "--static", action="store_false", dest="shared")
    if "test" in additional_choosers:
        parser.add_argument(
            "-t",
            "--test",
            action="store_true",
            help="Build tests",
            default=False,
        )
    return parser
