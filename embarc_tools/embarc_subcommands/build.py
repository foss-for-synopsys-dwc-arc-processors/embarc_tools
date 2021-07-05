from __future__ import print_function, division, unicode_literals
import os
import sys
from ..settings import get_input
from ..builder import build
from ..utils import getcwd


help = "Build application"
description = ("Compile code using toolchain.\n"
               "Currently supported Toolchain: GNU, MetaWare.")


def run(args, remainder=None):
    cached_config = args.config
    if not cached_config:
        if os.path.exists(os.path.join(args.outdir, "build.json")):
            cached_config = os.path.join(args.outdir, "build.json")
        elif os.path.exists(os.path.join(args.directory, "build.json")):
            cached_config = os.path.join(args.directory, "build.json")

    builder = build.embARC_Builder(
        source_dir=args.directory, build_dir=args.outdir,
        board=args.board, board_version=args.bd_ver,
        core=args.core, toolchain=args.toolchain,
        buildopts=args.build_opt,
        embarc_config=cached_config
    )
    if args.export:
        if os.path.exists(os.path.join(builder.build_dir, ".project")) and os.path.exists(os.path.join(builder.build_dir, ".cproject")):
            while True:
                yes = get_input("The IDE project already exists, recreate and overwrite the old files [Y/N]  ")
                if yes in ["yes", "Y", "y"]:
                    break
                elif yes in ["no", "n", "N"]:
                    return
                else:
                    continue
        builder.generate_ide()
        sys.exit(0)
    builder.build_target(args.target)


def setup(subparsers):
    subparser = subparsers.add_parser('build', help=help, description=description)
    subparser.add_argument(
        "-d", "--directory", default=getcwd(), help="application source directory", metavar='')
    subparser.add_argument(
        "-O", "--outdir", default=os.path.join(os.getcwd(), "build-out"),
        help="output directory for logs and binaries", metavar='')
    subparser.add_argument(
        "-b", "--board", help="choose board", metavar='')
    subparser.add_argument(
        "--bd-ver", help="choose board version", metavar='')
    subparser.add_argument(
        "--core", help="choose core", metavar='')
    subparser.add_argument(
        "--toolchain", choices=["mw", "gnu"], help="choose toolchain", metavar='')
    subparser.add_argument(
        "--target", default="all",
        help="choose build target, default target is all", metavar='')
    subparser.add_argument(
        "-g", "--export", action="store_true",
        help="generate eclipse project files, skip to build application")
    subparser.add_argument(
        "--config", help="specify application configuration, default is to look for build.json", metavar='')
    subparser.add_argument('-o', '--build-opt', default=[], action='append', metavar='',
                           help="""options to pass to the make command,
                           may be given more than once.
                           Example: OLEVEL=O2""")
    subparser.set_defaults(func=run)
