from __future__ import print_function, division, unicode_literals
import sys
import logging
from ...settings import get_input, SUPPORT_TOOLCHAIN
from ...osp import osp
from ...toolchain import gnu, metaware
from ...utils import read_json, generate_json

logger = logging.getLogger("toolchain - gnu")
logger.setLevel(logging.DEBUG)

help = "Get, set toolchain configuration options."
usage = ("\n    embarc config toolchain [--version] [--download] gnu\n"
         "    embarc config toolchain mw\n"
         "    embarc config toolchain --set <toolchain>\n")


def run(args, remainder=None):
    if len(remainder) == 1 and remainder[0] in SUPPORT_TOOLCHAIN:
        gnu_verion = gnu.Gnu.check_version()
        mw_verion = metaware.Mw.check_version()
        toolchain = remainder[0]
        if toolchain == "gnu":
            if gnu_verion:
                logger.info("Current GNU verion: {}".format(gnu_verion))
            else:
                toolchain_class = gnu.Gnu()
                input_ = None
                if not args.download:
                    input_ = get_input("[embARC] Download the latest gnu [Y/N]")
                if input_ in ["Y", "y", "yes"]:
                    input_ = True
                if input_ or args.download:
                    tgz_path = toolchain_class.download(version=args.version, path=args.download_path)
                    logger.info("Download it to : {}, please install it and set environment.".format(tgz_path))
                else:
                    logger.info("You can get GNU Toolchain from (%s)" % (toolchain_class.root_url))

        elif toolchain == "mw":
            if mw_verion:
                logger.info("Current MetaWare version: {}".format(mw_verion))
            else:
                logger.info("There is no MetaWare in this platform, please install it")
        else:
            logger.error("This toolchain {} is not supported now".format(toolchain))
            sys.exit(1)
    elif not remainder:
        if args.set:
            if args.set in SUPPORT_TOOLCHAIN:
                logger.info("Set %s as global TOOLCHAIN" % args.set)
                global_cfg = read_json(osp.GLOBAL_CFG_FILE)
                global_cfg["TOOLCHAIN"] = args.set
                generate_json(global_cfg, osp.GLOBAL_CFG_FILE)
            else:
                logger.error("Only support GNU and MetaWare now")
        else:
            logger.error("usage: " + usage)
    else:
        logger.error("usage: " + usage)


def setup(subparsers):
    subparser = subparsers.add_parser('toolchain', help=help)
    subparser.usage = usage
    subparser.add_argument(
        "--version", action='store_true', help="Choose toolchain version.")
    subparser.add_argument(
        "--download", action='store_true', help="Downlad the latested toolchain only support gnu.")
    subparser.add_argument(
        "--set", help="Set a toolchain as global setting.")
    subparser.set_defaults(func=run)
