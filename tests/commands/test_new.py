from __future__ import print_function, division
import pytest
import pexpect
import platform
from .conftest import runcmd
from embarc_tools.utils import cd

def test_new_commands(tmpdir, get_osp):
    testdir = tmpdir.mkdir("test")
    runcmd([ "new", "--help"])
    with cd(testdir.strpath):
        runcmd([ "new", "--board", "emsk", "--bd-ver", "22", "--core", "arcem7d", "--toolchain", "gnu", "hello"])
