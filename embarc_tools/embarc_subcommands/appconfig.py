from __future__ import print_function, division, unicode_literals
import sys
import os
from ..utils import getcwd, generate_json
from ..builder import build

help = "Get or set application config"
description = ("Show detail config.\n"
               "Currently supported options: board, board version, current core, toolchain, olevel and embarc root.\n"
               "Result is to look for embarc_app.json, default options in makefile will be overridden by it")


def run(args, remainder=None):
    if remainder:
        print("ERROR    - invalid parameter %s" % remainder[0])
        sys.exit(1)
    cached_config = args.config
    if not cached_config:
        if os.path.exists(os.path.join(args.outdir, "build.json")):
            cached_config = os.path.join(args.outdir, "build.json")
        elif os.path.exists(os.path.join(args.directory, "build.json")):
            cached_config = os.path.join(args.directory, "build.json")
    builder = build.embARC_Builder(
        source_dir=args.directory,
        build_dir=args.directory,
        board=args.board, board_version=args.bd_ver,
        core=args.core, toolchain=args.toolchain,
        embarc_root=args.embarc_root,
        embarc_config=cached_config
    )
    builder.setup_build()
    generate_json(builder.cache_configs, builder.embarc_config)


def setup(subparsers):
    subparser = subparsers.add_parser('appconfig', help=help, description=description)
    subparser.add_argument(
        "-d", "--directory", default=getcwd(), help="application path", metavar='')
    subparser.add_argument(
        "-O", "--outdir", default=os.path.join(os.getcwd(), "build-out"),
        help="output directory for logs and binaries. ", metavar='')
    subparser.add_argument(
        "-b", "--board", help="set board", metavar='')
    subparser.add_argument(
        "--bd-ver", help="set board version", metavar='')
    subparser.add_argument(
        "--core", help="set core", metavar='')
    subparser.add_argument(
        "--toolchain", choices=["mw", "gnu"], help="set toolchain", metavar='')
    subparser.add_argument(
        "--embarc-root", help="set embARC OSP root path", metavar='')
    subparser.add_argument(
        "--config", help="specify application configuration, default is to look for build.json", metavar='')
    subparser.set_defaults(func=run)
