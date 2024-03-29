from __future__ import print_function, division
import os
import pytest
import subprocess
from .conftest import runcmd
from embarc_tools.utils import cd, getcwd
from embarc_tools.osp import osp

def test_build_commands(tmpdir, get_osp):
    testdir = tmpdir.mkdir("test")
    runcmd([ "build", "--help"])
    with cd(testdir.strpath):
        runcmd([ "new", "--board", "emsk", "--bd-ver", "22", "--core", "arcem7d", "--toolchain", "gnu", "-d", "helloworld"])
        app_path = os.path.join(getcwd(), "helloworld")
        runcmd([ "build", "--directory", app_path, "--target", "clean"])
        runcmd([ "build", "--directory", app_path])
        runcmd([ "build", "--directory", app_path, "--target", "clean"])
        runcmd([ "build", "--directory", app_path, "--toolchain", "gnu"])
        runcmd([ "build", "--directory", app_path, "--target", "clean"])
        runcmd([ "build", "--directory", app_path, "--board", "emsk", "--bd-ver", "22", "--core", "arcem7d", "--toolchain", "gnu"])
        runcmd([ "build", "--directory", app_path, "--board", "emsk", "--bd-ver", "22", "--core", "arcem7d", "--toolchain", "gnu", "-g"])
        embarc_osp_cached_root = os.environ.get("EMBARC_OSP_CACHE_FOLDER")
        blinky = os.path.join(embarc_osp_cached_root, "example", "baremetal", "blinky")
        runcmd([ "build", "--directory", blinky, "--target", "clean"])
        runcmd([ "build", "--directory", blinky, "--board", "emsk", "--bd-ver", "22", "--core", "arcem7d", "--toolchain", "gnu"])
        runcmd([ "build", "--directory", blinky, "--board", "emsk", "--bd-ver", "22", "--core", "arcem7d", "--toolchain", "gnu", "-g"])

