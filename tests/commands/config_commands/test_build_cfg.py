from __future__ import print_function, division
import os
import pytest
import subprocess
from ..conftest import runcmd


@pytest.fixture
def test_new_commands():
	runcmd(["config", "build_cfg", "BOARD", "emsk"])
	runcmd(["config", "build_cfg", "BD_VER", "23"])
	runcmd(["config", "build_cfg", "CUR_CORE", "arcem7d"])