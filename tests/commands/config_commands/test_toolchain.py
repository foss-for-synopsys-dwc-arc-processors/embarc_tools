from __future__ import print_function, division
import os
import pytest
import subprocess
from ..conftest import runcmd
from embarc_tools.download_manager import cd, getcwd


def test_toolchain_commands(tmpdir):
    testdir = tmpdir.mkdir("test")
    with cd(testdir.strpath):

        runcmd(["config", "toolchain", "--version", "gnu"])
        runcmd(["config", "toolchain", "--set", "gnu"])
