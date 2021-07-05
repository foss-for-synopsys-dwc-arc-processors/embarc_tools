from __future__ import print_function, division, unicode_literals
import logging
import sys
from ...osp import osp
from ...utils import read_json, generate_json


help = "set global build configuration."
usage = ("\n    embarc config build_cfg BOARD <value>\n"
         "    embarc config build_cfg BD_VER <value>\n"
         "    embarc config build_cfg CUR_CORE <value>\n")


def run(args, remainder=None):
    if len(remainder) != 2:
        logging.error("usage: " + usage)
    else:
        config = remainder[0]
        if config not in ["BOARD", "BD_VER", "CUR_CORE"]:
            logging.error("usage: " + usage)
            sys.exit(1)
        value = remainder[1]
        global_cfg = read_json(osp.GLOBAL_CFG_FILE)
        logging.info("Set %s = %s as global setting" % (config, value))
        global_cfg["BUILD_CONFIG"][config] = value
        generate_json(global_cfg, osp.GLOBAL_CFG_FILE)


def setup(subparsers):
    subparser = subparsers.add_parser('build_cfg', help=help)
    subparser.usage = usage
    subparser.set_defaults(func=run)
