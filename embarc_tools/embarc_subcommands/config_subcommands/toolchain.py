from __future__ import print_function, division, unicode_literals
import os
import logging
from ...settings import SUPPORT_TOOLCHAIN
from ...osp import osp
from ...toolchain import gnu, metaware
from ...utils import read_json, generate_json


help = "get, set toolchain configuration options."
usage = ("\n    embarc config toolchain --version\n"
         "    embarc config toolchain --download <version>\n"
         "    embarc config toolchain --set <gnu/mw>")


def run(args, remainder=None):
    gnu_toolchain = gnu.Gnu()
    mw_toolchain = metaware.Mw()
    if args.version:
        if not gnu_toolchain.exe:
            logging.info("can't find gnu toolchain from current platform")
        else:
            version = gnu_toolchain.check_version()
            logging.info("current GNU version: {}".format(version))
        if not mw_toolchain.exe:
            logging.info("can't find Metaware toolchain from current platform")
        else:
            version = mw_toolchain.check_version()
            logging.info("current Metaware version: {}".format(version))
    if args.download:
        if not remainder:
            directory = os.getcwd()
        else:
            directory = remainder[0] or os.getcwd()
        version = args.download
        tgz_path = gnu_toolchain.download(version=version, path=directory)
        logging.info("download it to : {}, please install it and set environment.".format(tgz_path))
    if args.set:
        if args.set in SUPPORT_TOOLCHAIN:
            logging.info("set %s as global TOOLCHAIN" % args.set)
            global_cfg = read_json(osp.GLOBAL_CFG_FILE)
            global_cfg["TOOLCHAIN"] = args.set
            generate_json(global_cfg, osp.GLOBAL_CFG_FILE)
        else:
            logging.error("only support GNU and MetaWare now")


def setup(subparsers):
    subparser = subparsers.add_parser('toolchain', help=help)
    subparser.usage = usage
    mutualex_group = subparser.add_mutually_exclusive_group()
    mutualex_group.add_argument(
        "--version", action='store_true', help="show the version of supported toolchains")
    mutualex_group.add_argument(
        "--download", metavar='', help="downlad the specify version of toolchain, only support gnu")
    mutualex_group.add_argument(
        "--set", metavar='', help="set a toolchain as global setting")
    subparser.set_defaults(func=run)
