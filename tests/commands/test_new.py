from __future__ import print_function, division
import pytest
from .conftest import runcmd
from embarc_tools.utils import cd

def test_new_commands(tmpdir, get_osp):
	testdir = tmpdir.mkdir("test")
	with cd(testdir.strpath):
		runcmd([ "new", "--board", "emsk", "--bd-ver", "22", "--core", "arcem7d", "--toolchain", "gnu", "hello"])
