from __future__ import print_function, division
from ..conftest import runcmd


def test_build_cfg_commands():
    runcmd(["config", "--help"])
    runcmd(["config", "build_cfg", "--help"])
    runcmd(["config", "build_cfg", "BOARD", "emsk"])
    runcmd(["config", "build_cfg", "BD_VER", "23"])
    runcmd(["config", "build_cfg", "CUR_CORE", "arcem7d"])
