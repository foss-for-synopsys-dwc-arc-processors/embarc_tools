from __future__ import print_function, division
import os
import pytest
import subprocess
from .conftest import runcmd
from embarc_tools.utils import cd, getcwd


def test_appconfig_commands(tmpdir, get_osp):
    testdir = tmpdir.mkdir("test")
    with cd(testdir.strpath):
        runcmd(["new", "--quick"])
        app_path = os.path.join(getcwd(), "helloworld")
        runcmd(["appconfig", "--path", app_path])
        runcmd(["appconfig", "--path", app_path, "--toolchain", "gnu"])
