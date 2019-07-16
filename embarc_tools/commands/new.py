from __future__ import print_function, unicode_literals, unicode_literals
import os
import sys
import collections
from ..settings import get_input, SUPPORT_TOOLCHAIN, BUILD_CONFIG_TEMPLATE
from ..notify import (print_string, print_table)
from ..exporter import Exporter
from ..osp import osp
from ..utils import mkdir, getcwd, generate_json

help = "Create a new application"
description = ("Options can be input by command line parameter. \n"
               "via the --quick, it will get options from global settings.")
osppath = osp.OSP()


def run(args, remainder=None):
    if not args.application:
        if len(remainder) == 1:
            if remainder[0].startswith("-"):
                print("embarc new: error: invalid parameter %s" % remainder[0])
                sys.exit(1)
            args.application = remainder[0]
        elif len(remainder) > 1:
            print("embarc new: error: invalid parameter %s" % remainder[1])
            sys.exit(1)

    olevel = args.olevel
    config = build_config(args)
    application = config["APPL"]
    config["OLEVEL"] = olevel
    if not config:
        return
    # config["APPL"] = application
    print_string("Current configuration ")
    table_head = list()
    table_content = list()
    for key, value in config.items():
        table_head.append(key)
        table_content.append(value)
    print_table([table_head, [table_content]])

    app_path = os.path.join(getcwd(), application)
    config["EMBARC_OSP_ROOT"] = config["EMBARC_OSP_ROOT"].replace("\\", "/")
    app_json_path = os.path.join(app_path, "embarc_app.json")
    mkdir(app_path)
    generate_json(config, app_json_path)
    config["MIDDLEWARE"] = args.middleware
    config["APPL_CSRC_DIR"] = args.csrc
    config["APPL_ASMSRC_DIR"] = args.asmsrc
    config["APPL_INC_DIR"] = args.include
    config["APPL_DEFINES"] = args.defines
    config["OS_SEL"] = args.os
    config["LIB_SEL"] = args.library
    print_string("Start to generate makefile and main.c ")
    exporter = Exporter("application")
    exporter.gen_file_jinja("makefile.tmpl", config, "makefile", application)
    exporter.gen_file_jinja("main.c.tmpl", config, "main.c", application)
    print_string("Finish generate makefile and main.c, and they are in %s" % app_path)
    # if args.csrc != ".":
    #     mkdir(os.path.join(getcwd(), application, args.csrc))


def get_osp_root(input_root=None):
    if not input_root:
        input_root = osppath.get_global("EMBARC_OSP_ROOT")
    if not input_root:
        print_string("Can't get osp root from global settings")
        current_record = osppath.list_path(show=True, current=None)
        input_root = get_input("[embARC] Choose osp root path num or set another path as osp root: ")
        input_root = input_root.replace("\\", "/")
        global_name = None
        if current_record:
            if input_root in current_record:
                global_name = input_root
            else:
                if osppath.is_osp(input_root):
                    for name, value in current_record.items():
                        if value.get("directory", False) == input_root:
                            global_name = name
        if not global_name:
            if osppath.is_osp(input_root):
                name_root = get_input("[embARC] Name this path: ")
                if name_root:
                    global_name = name_root
                    source_type = "local"
                    url = os.path.abspath(input_root)
                    msg = "Add this local (%s) to user profile osp.json" % (url)
                    print_string(msg)
                    osppath.set_path(global_name, source_type, url)
            else:
                msg = "What you choose is not a valid osp root"
                print_string(msg, level="warning")
                sys.exit(1)
        if global_name:
            print_string("Set %s as global EMBARC_OSP_ROOT" % global_name)
            config = "EMBARC_OSP_ROOT"
            osppath.set_global(config, global_name)

    if not osppath.is_osp(input_root):
        input_root = osppath.get_path(input_root)
    osp_root = input_root if osppath.is_osp(input_root) else None
    if not osp_root:
        msg = "What you choose is not a valid osp root"
        print_string(msg, level="warning")
        sys.exit(1)
    print_string("Current osp root is: " + osp_root)
    return osp_root


def build_config(args):
    config = dict()
    config = collections.OrderedDict()
    application = args.application

    osp_root = get_osp_root(args.osp_root)
    support_board = osppath.supported_boards(osp_root)

    if args.quick:
        config["APPL"] = application if application else str("helloworld")
        board = osppath.get_global("BOARD")
        if not board:
            board = str("emsk") if str("emsk") in support_board else support_board[0]
        config["BOARD"] = board
        bd_ver = osppath.get_global("BD_VER")
        if not bd_ver:
            bd_ver = osppath.supported_bd_versions(osp_root, board)[-1]
        config["BD_VER"] = bd_ver
        cur_core = osppath.get_global("CUR_CORE")
        if not cur_core:
            cur_core = osppath.supported_cores(osp_root, board, bd_ver)[0]
        config["CUR_CORE"] = cur_core
        toolchain = osppath.get_global("TOOLCHAIN")
        if not toolchain:
            toolchain = SUPPORT_TOOLCHAIN[0]
        config["TOOLCHAIN"] = toolchain
        config["EMBARC_OSP_ROOT"] = os.path.abspath(osp_root)
        return config

    if not application:
        while True:
            application = get_input("[embARC] Input application name: ")
            if application == "":
                print_string("Please don't set applcation name as a empty string ")
                application = None
                continue
            else:
                break

    board = args.board
    bd_ver = args.bd_ver
    cur_core = args.core
    toolchain = args.toolchain
    config = BUILD_CONFIG_TEMPLATE
    config["EMBARC_OSP_ROOT"] = str()
    config = collections.OrderedDict()
    config["APPL"] = application

    print_string("Support boards : {}".format("  ".join(support_board)))
    while True:
        if not board:
            board = get_input("[embARC] Choose board: ")
        if board not in support_board:
            board = None
            print_string("Please choose board from {}" .format(support_board))
            continue
        else:
            break
    config["BOARD"] = board
    support_bd_ver = osppath.supported_bd_versions(osp_root, board)
    print_string("{} support versions : {}".format(board, "  ".join(support_bd_ver)))
    while True:
        if not bd_ver:
            bd_ver = get_input("[embARC] Choose board version: ")
        if bd_ver not in support_bd_ver:
            bd_ver = None
            print_string("Please choose version from {}" .format(support_bd_ver))
            continue
        else:
            break
    config["BD_VER"] = bd_ver

    support_core = osppath.supported_cores(osp_root, board, bd_ver)
    print_string("{} with versions {} support cores : {}".format(board, bd_ver, "  ".join(support_core)))
    while True:
        if not cur_core:
            cur_core = get_input("[embARC] Choose core: ")
        if cur_core not in support_core:
            cur_core = None
            print_string("Please choose core from {}" .format(support_core))
            continue
        else:
            break
    config["CUR_CORE"] = cur_core
    support_toolchains = osppath.supported_toolchains(osp_root)
    print_string("Support toolchains: {}".format("  ".join(support_toolchains)))
    while True:
        if not toolchain:
            toolchain = get_input("[embARC] Choose toolchain: ")
        if toolchain not in support_toolchains:
            toolchain = None
            print_string("Please choose toolchain from {}" .format(support_toolchains))
            continue
        else:
            break
    config["TOOLCHAIN"] = toolchain
    config["EMBARC_OSP_ROOT"] = os.path.abspath(osp_root)
    return config


def setup(subparser):
    subparser.add_argument(
        "-a", "--application", help="specify the path of the application", metavar='')
    subparser.add_argument(
        "-b", "--board", help="choose board", metavar='')
    subparser.add_argument(
        "--bd_ver", help="choose board version", metavar='')
    subparser.add_argument(
        "--core", help="choose core", metavar='')
    subparser.add_argument(
        "--toolchain", choices=["mw", "gnu"], help="choose toolchain", metavar='')
    subparser.add_argument(
        "--osp_root", help="set embARC OSP root path", metavar='')
    subparser.add_argument(
        "-o", "--olevel", default="O3", choices=["Os", "O0", "O1", "O2"], help="set olevel", metavar='')
    subparser.add_argument(
        '-m', '--middleware', action='store', default="common", help='choose a middleware', metavar='')
    subparser.add_argument(
        '--csrc', action='store', default=".", help='specify the path of application C source dirs', metavar='')
    subparser.add_argument(
        '--asmsrc', action='store', default=".", help='specify the path of application assembly source dirs', metavar='')
    subparser.add_argument(
        '--include', action='store', default=".", help='specify the path of application include dirs', metavar='')
    subparser.add_argument(
        '--defines', action='store', default=".", help='application defines', metavar='')
    subparser.add_argument(
        '--os', action='store', default="", help='choose operation system', metavar='')
    subparser.add_argument(
        '--library', action='store', default="", help='choose library', metavar='')
    subparser.add_argument(
        '--quick', action='store_true', default="", help='create application quickly with default configuration')
