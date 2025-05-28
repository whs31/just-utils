import argparse

def default_cmake_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode', default=False)
    parser.add_argument('-c', '--clean', action='store_true', help='clean build directory', default=False)
    parser.add_argument('-C', '--configure', action='store_true', help='reconfigure cmake only (no build)', default=False)
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
    return parser