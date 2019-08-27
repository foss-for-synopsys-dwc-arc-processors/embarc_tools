from __future__ import print_function, division, unicode_literals
import os
import sys
from ..project import Generator
from ..settings import get_input, get_config
from ..builder import build
from ..utils import cd, getcwd, read_json
help = "Build application"
description = ("Compile code using toolchain.\n"
               "Currently supported Toolchain: GNU, MetaWare.")


def run(args, remainder=None):
    osproot = None
    app_path = args.path
    recordBuildConfig = dict()
    app_path = os.path.abspath(app_path)

    if not (os.path.exists(app_path) and os.path.isdir(app_path)):
        print("[embARC] This is not a valid application path")
        return

    embarc_config = args.app_config

    if not (embarc_config and os.path.exists(embarc_config)):
        embarc_config = os.path.join(app_path, "embarc_app.json")

    if os.path.exists(embarc_config):
        print("[embARC] Read embarc_app.json")
        recordBuildConfig = read_json(embarc_config)

    parallel = args.parallel
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
    if remainder:
        if (remainder[0]).startswith("-"):
            print("embarc build: error: invalid parameter %s" % remainder[0])
            sys.exit(1)
        make_config, target = get_config(remainder)
        if target:
            args.target = target
        recordBuildConfig.update(make_config)

    builder = build.embARC_Builder(osproot, recordBuildConfig, args.outdir)
    if args.export:
        builder.get_build_cmd(app_path, target=None, parallel=parallel, silent=False)
        with cd(app_path):
            if os.path.exists(".project") and os.path.exists(".cproject"):
                while True:
                    yes = get_input("The IDE project already exists, recreate and overwrite the old files [Y/N]  ")
                    if yes in ["yes", "Y", "y"]:
                        break
                    elif yes in ["no", "n", "N"]:
                        return
                    else:
                        continue
            generator = Generator()
            recordBuildConfig = read_json(embarc_config)
            for project in generator.generate(buildopts=recordBuildConfig):
                project.generate()
        sys.exit(0)
    if args.target:
        information = None
        if args.target == "elf":
            information = builder.build_elf(app_path, parallel=parallel, pre_clean=False, post_clean=False)
        elif args.target == "bin":
            information = builder.build_bin(app_path, parallel=parallel, pre_clean=False, post_clean=False)
        elif args.target == "hex":
            information = builder.build_hex(app_path, parallel=parallel, pre_clean=False, post_clean=False)
        elif args.target == "clean":
            information = builder.clean(app_path, parallel=parallel)
        elif args.target == "distclean":
            information = builder.distclean(app_path, parallel=parallel)
        elif args.target == "boardclean":
            information = builder.boardclean(app_path, parallel=parallel)
        elif args.target == "info":
            information = builder.get_build_info(app_path, parallel=parallel)
        elif args.target == "size":
            information = builder.get_build_size(app_path, parallel=parallel)
        elif args.target:
            information = builder.build_target(app_path, target=args.target, parallel=parallel, coverity=False)
        else:
            print("[embARC] Please choose right target")
        if information:
            if information.get("result") is False:
                print("[embARC] Failed: {}".format(information.get("reason")))


def setup(subparser):
    subparser.add_argument(
        "-d", "--path", default=getcwd(), help="application path", metavar='')
    subparser.add_argument(
        "--outdir", help="output objs root directory", metavar='')
    subparser.add_argument(
        "-b", "--board", help="choose board", metavar='')
    subparser.add_argument(
        "--bd_ver", help="choose board version", metavar='')
    subparser.add_argument(
        "--core", help="choose core", metavar='')
    subparser.add_argument(
        "-o", "--olevel", default="O3", choices=["Os", "O0", "O1", "O2", "O3"], help="set olevel", metavar='')
    subparser.add_argument(
        "--toolchain", choices=["mw", "gnu"], help="choose toolchain", metavar='')
    subparser.add_argument(
        "-j", "--parallel", type=int, help="build application with -j", metavar='')
    subparser.add_argument(
        "--target", default="all",
        help="choose build target, default target is all", metavar='')
    subparser.add_argument(
        "-g", "--export", action="store_true", help="generate IDE project files for your application")
    subparser.add_argument(
        "--app_config", help="specify application configuration, default is to look for embarc_app.json", metavar='')
