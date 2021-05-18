from __future__ import print_function, division
import os
import pytest
import subprocess
from .conftest import runcmd
from embarc_tools.utils import cd, getcwd


def test_appconfig_commands(tmpdir, get_osp):
    testdir = tmpdir.mkdir("test")
    runcmd([ "appconfig", "--help"])
    with cd(testdir.strpath):
        runcmd([ "new", "--board", "emsk", "--bd-ver", "22", "--core", "arcem7d", "--toolchain", "gnu", "-d", "helloworld"])
        app_path = os.path.join(getcwd(), "helloworld")
        runcmd(["appconfig", "--directory", app_path])
        runcmd(["appconfig", "--directory", app_path, "--toolchain", "gnu"])
