from __future__ import print_function, division
import os
import pytest
import subprocess
from conftest import runcmd
from embarc_tools.download_manager import cd, getcwd


@pytest.fixture
def test_new_commands(tmpdir):
	testdir = tmpdir.mkdir("test")
	with cd(testdir):
		runcmd(["new", "--quick"])
		app_path = os.path.join(getcwd(), "helloworld")
		runcmd(["appconfig", "--application", app_path])
		runcmd(["appconfig", "--application", app_path, "--toolchain", "gnu"])
