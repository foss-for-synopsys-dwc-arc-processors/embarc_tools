from __future__ import print_function, division
import os
import pytest
import subprocess
from conftest import runcmd
from embarc_tools.download_manager import cd


@pytest.fixture
def test_new_commands(tmpdir):
    testdir = tmpdir.mkdir("test")
    with cd(testdir):
        runcmd(["new", "--board", "emsk", "--bd_ver", "22", "--cur_core", "arcem7d"])
        runcmd(["new", "--toolchain", "gnu"])
        runcmd(["new", "--quick"])
