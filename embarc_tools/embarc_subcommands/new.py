from __future__ import print_function, unicode_literals, unicode_literals
import os
import logging
import glob
from ..settings import get_input
from ..generator import Exporter
from ..osp import osp, platform
from ..utils import generate_json, read_json


help = "Create a new application"
description = ("Options can be input by command line parameter. \n")
osppath = osp.OSP()


def get_osp_root(input_root=None):
    embarc_root = None
    if not input_root:
        cur_global_cfg = read_json(osppath.global_cfg_file)
        input_root = cur_global_cfg["EMBARC_ROOT"]
        embarc_root = input_root
    if not input_root:
        logging.info("Can't get osp root from global settings")
        current_record = osppath.list()
        while True:
            input_root = get_input("Choose osp root path name or set another path as osp root: ")
            input_root = input_root.replace("\\", "/")
            if osppath.is_osp(input_root):
                embarc_root = input_root
            elif current_record:
                if input_root in current_record:
                    embarc_root = current_record[input_root]["directory"]
            if osppath.is_osp(embarc_root):
                cur_global_cfg["EMBARC_ROOT"] = embarc_root
                generate_json(cur_global_cfg, osppath.global_cfg_file)
                break
            logging.error("What you choose is not a valid osp root")
    return embarc_root


def find_platform(args, appl_dir, config):
    global_build_cfg = read_json(osppath.global_cfg_file)["BUILD_CONFIG"]
    board = args.board or global_build_cfg["BOARD"]
    if not board:
        for file in glob.glob(os.path.join(config["EMBARC_ROOT"], "board", "*", "*.mk")):
            try:
                boards = os.path.splitext(os.path.basename(file))
                while True:
                    logging.info("please choose board from {}" .format(boards))
                    board = get_input("choose board: ")
                    if board not in boards:
                        continue
                    break
                break
            except RuntimeError as e:
                logging.error("E: failed to find a board. %s" % e)
    plat = platform.Platform(board, args.bd_ver, args.core)
    config["BOARD"] = plat.name
    exporter = Exporter("application")
    exporter.gen_file_jinja("makefile.tmpl", config, "makefile", appl_dir)
    exporter.gen_file_jinja("main.c.tmpl", config, "main.c", appl_dir)
    plat.version = args.bd_ver or global_build_cfg["BD_VER"]
    if not plat.version:
        versions = plat.get_versions(appl_dir, config["EMBARC_ROOT"])
        while True:
            logging.info("please choose board version from {}".format(" ".join(versions)))
            plat.version = get_input("choose version: ")
            if plat.version not in versions:
                continue
            break
    config["BD_VER"] = plat.version
    plat.core = args.core or global_build_cfg["CUR_CORE"]
    if not plat.core:
        cores = plat.get_cores(plat.version, appl_dir, config["EMBARC_ROOT"])
        while True:
            logging.info("please choose board core from {}".format(" ".join(cores)))
            plat.core = get_input("choose version: ")
            if plat.core not in cores:
                continue
            break
    config["CUR_CORE"] = plat.core
    logging.info("platform: {}".format(plat))
    return config


def run(args, remainder=None):
    config = dict()
    appl_dir = os.path.abspath(args.directory or os.getcwd()).replace("\\", "/")
    os.makedirs(appl_dir, exist_ok=True)

    config["APPL"] = os.path.basename(appl_dir)
    logging.info("application: {} in {}".format(config["APPL"], appl_dir))
    config["APPL_CSRC_DIR"] = "."
    config["APPL_ASMSRC_DIR"] = "."
    config["APPL_INC_DIR"] = "."

    config["EMBARC_ROOT"] = get_osp_root(args.embarc_root)
    logging.info("embarc_root: {}".format(config["EMBARC_ROOT"]))

    logging.info("toolchain: {}".format(args.toolchain))
    config["TOOLCHAIN"] = args.toolchain

    config = find_platform(args, appl_dir, config)

    generate_json(config, os.path.join(appl_dir, "build.json"))
    logging.info("cache build config into %s" % os.path.join(appl_dir, "build.json"))
    if args.build_opt:
        logging.info("parse extra build options")
        for opt in args.build_opt:
            if "=" in opt:
                (key, value) = opt.split("=")
                logging.info("{}: {}".format(key, value))
                if key in ["APPL_CSRC_DIR", "APPL_ASMSRC_DIR", "APPL_INC_DIR"]:
                    config[key] = "{} {}".format(config[key], value.replace("\\", "/"))
                else:
                    config[key] = value

    exporter = Exporter("application")
    exporter.gen_file_jinja("makefile.tmpl", config, "makefile", appl_dir)
    exporter.gen_file_jinja("main.c.tmpl", config, "main.c", appl_dir)
    logging.info("finish to genrate application")


def setup(subparsers):
    subparser = subparsers.add_parser('new', help=help, description=description)
    subparser.add_argument(
        "-b", "--board", help="choose board", metavar='')
    subparser.add_argument(
        "--bd-ver", help="choose board version", metavar='')
    subparser.add_argument(
        "--core", help="choose core", metavar='')
    subparser.add_argument(
        "--toolchain", choices=["mw", "gnu"], default="gnu", help="choose toolchain", metavar='')
    subparser.add_argument(
        "--embarc-root", help="set embARC OSP root path", metavar='')
    subparser.add_argument('-o', '--build-opt', default=[], action='append',
                           help='''options to pass to the build tool make
                           may be given more than once''')
    subparser.add_argument(
        "-d", "--directory", help="specify the root of the application", metavar='')
    subparser.set_defaults(func=run)
