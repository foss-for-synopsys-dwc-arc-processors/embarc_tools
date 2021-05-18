from __future__ import print_function, division
from ..conftest import runcmd


def test_osp_commands(get_osp):
    runcmd(["config", "--help"])
    runcmd(["config", "osp", "--help"])
    runcmd(["config", "osp", "--list"])
