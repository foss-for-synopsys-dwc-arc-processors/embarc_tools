from __future__ import print_function, division
from ..conftest import runcmd


def test_osp_commands(get_osp):
    runcmd(["config", "osp", "--list"])
