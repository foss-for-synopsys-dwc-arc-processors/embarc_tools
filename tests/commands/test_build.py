from __future__ import print_function, division
import os
import pytest
import subprocess
from conftest import runcmd
from embarc_tools.download_manager import cd, getcwd


@pytest.fixture
def test_new_commands(tmpdir, get_osp):
	testdir = tmpdir.mkdir("test")
	with cd(testdir):
		runcmd(["new", "--quick"])
		app_path = os.path.join(getcwd(), "helloworld")
		runcmd(["build", "--path", app_path, "--toolchain", "gnu"])
		runcmd(["build", "--path", app_path, "--board", "emsk", "--bd_ver", "22", "--core", "arcem7d", "--toolchain", "gnu"])
		runcmd(["build", "--path", app_path, "BOARD=emsk", "BD_VER=23", "CUR_CORE=arcem9d", "TOOLCHAIN=gnu", "elf"])
		runcmd(["build", "--path", app_path, "-j", 4, "BOARD=emsk", "BD_VER=23", "CUR_CORE=arcem9d", "TOOLCHAIN=gnu", "elf"])
