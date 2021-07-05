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
        if platform.system() == "Linux":
            command = "embarc new --directory test_new_command"
            new_target = pexpect.spawn(command, encoding='utf-8')
            while True:
                child = new_target.expect("please choose .* from .*", timeout=90)
                output = new_target.before
                if child == 0:
                    to_input = (output.split())[-1]
                    child.sendline(to_input)
                    if child.expect("finish to genrate application", timeout=90):
                        break
                else:
                    break
