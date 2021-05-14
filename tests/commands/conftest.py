from __future__ import print_function, division
import os
import subprocess
import threading
import git
import pytest
from embarc_tools.settings import EMBARC_OSP_URL, CURRENT_PLATFORM
from embarc_tools.osp import osp
from embarc_tools.utils import cd, getcwd, delete_dir_files
from embarc_tools.toolchain import gnu

class ProcessException(Exception):
    pass

def _output_reader(proc):
    
    for line in iter(proc.stdout.readline, b''):
        print(line.decode('utf-8').rstrip())

def runcmd(command, **kwargs):
    env = os.environ.copy()
    pre_command = ["python", os.path.join(os.environ.get("SOURCE_PATH"), "main.py")]
    pre_command.extend(command)
    print("test command: {}".format(" ".join(pre_command)))
    with subprocess.Popen(pre_command, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, **kwargs) as proc:
        t = threading.Thread(target=_output_reader, args=(proc,), daemon=True)
        t.start()
        t.join()
        proc.wait()
        if proc.returncode != 0:
            raise ProcessException(proc.returncode, command[0], ' '.join(command), getcwd())

@pytest.fixture()
def get_osp():
    toolchain_root = os.environ.get("TOOLCHAIN_CACHE_FOLDER")
    store_gnu_toolchain(toolchain_root)
    embarc_osp_cached_root = os.environ.get("EMBARC_OSP_CACHE_FOLDER")
    is_osp_exists = False
    if os.path.exists(embarc_osp_cached_root):
        try:
            _ = git.Repo(embarc_osp_cached_root).git_dir
            repo = git.cmd.Git(embarc_osp_cached_root)
            repo.pull()
            osppath = osp.OSP()
            if osppath.is_osp(embarc_osp_cached_root):
                is_osp_exists = True
        except git.exc.InvalidGitRepositoryError:
            delete_dir_files(embarc_osp_cached_root, dir=True)
    if not is_osp_exists:
        if os.path.exists(embarc_osp_cached_root):
            delete_dir_files(embarc_osp_cached_root, dir=True)
        runcmd(["config", "osp", "--add", "new_osp", "-m", EMBARC_OSP_URL, "--mr", "master", embarc_osp_cached_root])
        runcmd(["config", "osp", "--set", "new_osp"])
    app_path = os.path.join(getcwd(), "helloworld")
    if not os.path.exists(app_path):
        runcmd([ "new", "--board", "emsk", "--bd-ver", "22", "--core", "arcem9d", "--toolchain", "gnu", "-d", "helloworld"])

def store_gnu_toolchain(path):
    gnu_toolchain = gnu.Gnu()
    if gnu_toolchain.exe:
        return None

    version = "2020.09"
    if CURRENT_PLATFORM == "Linux":
        gnu_tgz_path = gnu_toolchain.download(version, path)
        gnu_file_path = None
        if gnu_tgz_path is None:
            print("Can't download gnu {} ".format(version))
        else:
            gnu_file_path = gnu_toolchain.extract_file(gnu_tgz_path, path)
            os.environ["ARC_GNU_ROOT"] = gnu_file_path
            os.environ["PATH"] = os.environ["PATH"] + ":" + gnu_file_path + "/bin"