from __future__ import print_function, unicode_literals
import platform
import sys
import os

EMBARC_OSP_URL = "https://github.com/foss-for-synopsys-dwc-arc-processors/embarc_osp.git"
OSP_DIRS = ["arc", "board", "device", "include", "library", "middleware"]
OLEVEL = ["Os", "O0", "O1", "O2", "O3"]
GNU_PATH = ""
MW_PATH = ""
SUPPORT_TOOLCHAIN = ["gnu", "mw"]
OSP_PATH = ""
CURRENT_PLATFORM = platform.system()
PYTHON_VERSION = platform.python_version()
MAKEFILENAMES = ['Makefile', 'makefile', 'GNUMakefile']
MIDDLEWARE = [
    "aws",
    "coap",
    "common",
    "fatfs",
    "http_parser",
    "ihex",
    "lwip-contrib",
    "Lwip",
    "mbedtls",
    "mqtt",
    "ntshell",
    "openthread",
    "parson",
    "u8glib",
    "wakaama"
]

LIBRARIES = ["clib", "secureshield"]

BUILD_CONFIG_TEMPLATE = {
    "APPL": "",
    "BOARD": "",
    "BD_VER": "",
    "CUR_CORE": "",
    "TOOLCHAIN": "",
    "OLEVEL": "",
}

BUILD_OPTION_NAMES = ['BOARD', 'BD_VER', 'CUR_CORE', 'TOOLCHAIN', 'OLEVEL', 'V', 'DEBUG', 'SILENT', 'JTAG']
BUILD_INFO_NAMES = ['EMBARC_ROOT', 'OUT_DIR_ROOT', 'BUILD_OPTION', 'APPLICATION_NAME', 'APPLICATION_LINKSCRIPT', 'APPLICATION_ELF', 'APPLICATION_BIN', 'APPLICATION_HEX', 'APPLICATION_MAP', 'APPLICATION_DUMP', 'APPLICATION_DASM', 'MIDDLEWARE', 'PERIPHERAL']
BUILD_CFG_NAMES = ['EMBARC_ROOT', 'OUT_DIR_ROOT', 'COMPILE_OPT', 'CXX_COMPILE_OPT', 'ASM_OPT', 'AR_OPT', 'LINK_OPT', 'DEBUGGER', 'DBG_HW_FLAGS', 'MDB_NSIM_OPT']
BUILD_SIZE_SECTION_NAMES = ['text', 'data', 'bss']


def get_input(input_str):
    try:
        return input(input_str)
    except KeyboardInterrupt:
        print("user aborted!")
        sys.exit(255)


def get_config(config):
    make_config = dict()
    target = None
    if config:
        for key in config:
            if "=" in key:
                config_pair = key.split("=")
                make_config[config_pair[0]] = config_pair[1]
            else:
                target = key
    return make_config, target


def is_embarc_makefile(makefile):
    embarc_root = None
    appl = None
    find_embarc_root = False
    find_appl = False
    with open(makefile) as f:
        lines = f.read().splitlines()
        for line in lines:
            if "EMBARC_ROOT" in line:
                embarc_root = (line.split("=")[1]).strip()
                find_embarc_root = True
            if "APPL" in line:
                appl = (line.split("=")[1]).strip()
                find_appl = True
            if find_embarc_root and find_appl:
                break
    return (find_embarc_root and find_appl), embarc_root, appl


def is_embarc_base(path):
    if os.path.exists(path) and os.path.isdir(path):
        for files in OSP_DIRS:
            files_path = os.path.join(path, files)
            if os.path.exists(files_path) and os.path.isdir(files_path):
                pass
            else:
                return False
        return True
    else:
        return False
