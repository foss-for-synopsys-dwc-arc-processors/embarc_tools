from __future__ import print_function, division, unicode_literals
from ..utils import import_submodules
from ..embarc_subcommands import config_subcommands


SUBCOMMANDS = import_submodules(config_subcommands, recursive=False)

help = "get, set or unset configuration options."

description = ("currently supported options: osp, toolchain, build_cfg")


def run(args, remainder=None):
    pass


def setup(subparsers):
    subparser = subparsers.add_parser('config', help=help, description=description)
    subparser.usage = ("\n    embarc config osp --add <name> -m <url> --mr <rev> [<dest>]\n"
                       "    embarc config osp --add <name> --local <dest> \n"
                       "    embarc config osp --rename <oldname> <newname>\n"
                       "    embarc config osp --remove <name>\n"
                       "    embarc config osp --list\n"
                       "    embarc config osp --set <name>\n"
                       "    embarc config toolchain --version\n"
                       "    embarc config toolchain --download <version>\n"
                       "    embarc config toolchain --set <gnu/mw>\n"
                       "    embarc config build_cfg BOARD <value>\n"
                       "    embarc config build_cfg BD_VER <value>\n"
                       "    embarc config build_cfg CUR_CORE <value>\n")
    subparser.set_defaults(func=run)

    # set up its sub commands
    config_subparsers = subparser.add_subparsers(title="Commands", metavar="           ")
    for _, subcommand in SUBCOMMANDS.items():
        subcommand.setup(config_subparsers)
