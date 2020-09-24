from __future__ import print_function, division, unicode_literals
import os
import sys
from ..notify import print_string
from ..utils import getcwd, read_json
from ..builder import build

help = "Get or set application config"
description = ("Show detail config.\n"
               "Currently supported options: board, board version, current core, toolchain, olevel and embarc root.\n"
               "Result is to look for embarc_app.json, default options in makefile will be overridden by it")


def run(args, remainder=None):
    if remainder:
        print("[embARC] embarc appconfig: error: invalid parameter %s" % remainder[0])
        sys.exit(1)

    builder = build.embARC_Builder()
    result = builder.build_common_check(args.path)
    if result["result"]:
        recordBuildConfig = dict()
        builder.build_dir = result["app_path"]
        embarc_config = os.path.join(builder.build_dir, "embarc_app.json")
        if os.path.exists(embarc_config):
            print("[embARC] Read embarc_app.json")
            recordBuildConfig = read_json(embarc_config)
        if args.board:
            recordBuildConfig["BOARD"] = args.board
        if args.bd_ver:
            recordBuildConfig["BD_VER"] = args.bd_ver
        if args.core:
            recordBuildConfig["CUR_CORE"] = args.core
        if args.toolchain:
            recordBuildConfig["TOOLCHAIN"] = args.toolchain
        if args.olevel:
            recordBuildConfig["OLEVEL"] = args.olevel
        if args.osp_root:
            osp_root, _ = osppath.check_osp(args.osp_root)
            builder.osproot = osp_root.replace("\\", "/")
        builder.buildopts.update(recordBuildConfig)
        build_config_template = builder.get_build_template()
        builder.get_makefile_config(build_config_template)

    else:
        print_string("[embARC] %s" % result["reason"])
        return


def setup(subparsers):
    subparser = subparsers.add_parser('appconfig', help=help, description=description)
    subparser.add_argument(
        "-d", "--path", default=getcwd(), help="application path", metavar='')
    subparser.add_argument(
        "-b", "--board", help="set board", metavar='')
    subparser.add_argument(
        "--bd_ver", help="set board version", metavar='')
    subparser.add_argument(
        "--core", help="set core", metavar='')
    subparser.add_argument(
        "--toolchain", choices=["mw", "gnu"], help="set toolchain", metavar='')
    subparser.add_argument(
        "--osp_root", help="set embARC OSP root path", metavar='')
    subparser.add_argument(
        "-o", "--olevel", default="O3", choices=["Os", "O0", "O1", "O2", "O3"], help="set olevel", metavar='')
    subparser.set_defaults(func=run)
