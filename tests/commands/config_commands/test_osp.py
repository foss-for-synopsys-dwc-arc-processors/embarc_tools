from __future__ import print_function, division
import os
import pytest
import subprocess
from ..conftest import runcmd


def test_osp_commands(get_osp):
    runcmd(["config", "osp", "--list"])
    runcmd(["config", "osp", "--rename", "new_osp", "rename"])
    runcmd(["config", "osp", "--list"])
    runcmd(["config", "osp", "--rename", "rename", "new_osp"])
