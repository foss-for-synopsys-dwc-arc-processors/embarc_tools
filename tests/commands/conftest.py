from __future__ import print_function, division
import os
import subprocess
import errno
import pytest
from embarc_tools.settings import EMBARC_OSP_URL, CURRENT_PLATFORM
from embarc_tools.osp import osp
from embarc_tools.utils import getcwd, mkdir
from embarc_tools.toolchain import gnu

class ProcessException(Exception):
    pass

def runcmd(command, **kwargs):

    pre_command = ["python", os.path.join(os.environ.get("SOURCE_PATH"), "main.py")]
    proc = None
    try:
        pre_command.extend(command)
        proc = subprocess.Popen(pre_command, **kwargs)
    except OSError as e:
        if e.args[0] == errno.ENOENT:
            print(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (command[0], command[0]), e.args[0])
        else:
            raise e

    if proc and proc.wait() != 0:
        raise ProcessException(proc.returncode, command[0], ' '.join(command), getcwd())

@pytest.fixture()
def get_osp():
    toolchain_root = os.environ.get("TOOLCHAIN_CACHE_FOLDER")
    store_gnu_toolchain(toolchain_root)
    current_path = getcwd()
    runcmd(["config", "osp", "--add", "new_osp", EMBARC_OSP_URL])
    runcmd(["config", "osp", "--set", "new_osp"])

    app_path = os.path.join(current_path, "helloworld")
    if not os.path.exists(app_path):
        runcmd(["new", "--quick"])

def store_gnu_toolchain(path):
    gnu_toolchain = gnu.Gnu()
    if gnu_toolchain.check_version():
        return None

    version = None
    if CURRENT_PLATFORM == "Linux":
        gnu_tgz_path = gnu_toolchain.download(version, path)
        gnu_file_path = None
        if gnu_tgz_path is None:
            print("Can't download gnu {} ".format(version))
        else:
            gnu_file_path = gnu_toolchain.extract_file(gnu_tgz_path, path)
            os.environ["ARC_GNU_ROOT"] = gnu_file_path
            os.environ["PATH"] = os.environ["PATH"] + ":" + gnu_file_path + "/bin"