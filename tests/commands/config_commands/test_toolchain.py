from __future__ import print_function, division
import os
import pytest
import subprocess
from ..conftest import runcmd
from embarc_tools.utils import cd, getcwd


def test_toolchain_commands(tmpdir, get_osp):
    testdir = tmpdir.mkdir("test")
    runcmd(["config", "--help"])
    runcmd(["config", "toolchain", "--help"])
    with cd(testdir.strpath):
        runcmd(["config", "toolchain", "--version"])
        runcmd(["config", "toolchain", "--set", "gnu"])
