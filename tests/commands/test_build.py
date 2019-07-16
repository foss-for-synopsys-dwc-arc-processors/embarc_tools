from __future__ import print_function, division
import os
import pytest
import subprocess
from .conftest import runcmd
from embarc_tools.utils import cd, getcwd
from embarc_tools.osp import osp

def test_build_commands(tmpdir, get_osp):
    testdir = tmpdir.mkdir("test")
    with cd(testdir.strpath):
        runcmd([ "new", "--quick"])
        app_path = os.path.join(getcwd(), "helloworld")
        runcmd([ "build", "--path", app_path, "--toolchain", "gnu"])
        runcmd([ "build", "--path", app_path, "--board", "emsk", "--bd_ver", "22", "--core", "arcem7d", "--toolchain", "gnu"])
        runcmd([ "build", "--path", app_path, "BOARD=emsk", "BD_VER=23", "CUR_CORE=arcem9d", "TOOLCHAIN=gnu", "elf"])
        runcmd([ "build", "--path", app_path, "-j", "4", "BOARD=emsk", "BD_VER=23", "CUR_CORE=arcem9d", "TOOLCHAIN=gnu", "elf"])
    app_path = "example/baremetal/secureshield/secret_normal"
    osp_class = osp.OSP()
    embarc_root = osp_class.get_path("new_osp")
    app_path = os.path.join(embarc_root, "example/baremetal/secureshield/secret_normal")
    runcmd(["build", "--path", app_path, "--board", "iotdk", "--bd_ver", "10", "--core", "arcem9d", "--toolchain", "gnu"])
