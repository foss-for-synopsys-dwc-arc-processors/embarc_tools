from __future__ import print_function, division
import os
import shlex
import pytest
from embarc_tools.osp import osp


def check_output(*args, **kwargs):
    try:
        out_bytes = subprocess.check_output(*args, **kwargs)
    except subprocess.CalledProcessError as e:
        print('*** check_output: nonzero return code', e.returncode,
              file=sys.stderr)
        print('cwd =', os.getcwd(), 'args =', args,
              'kwargs =', kwargs, file=sys.stderr)
        print('subprocess output:', file=sys.stderr)
        print(e.output.decode(), file=sys.stderr)
        raise
    return out_bytes.decode(sys.getdefaultencoding())

def runcmd(cmd, cwd=None, stderr=None):
    try:
        cmd = " ".join(cmd)
        return check_output(shlex.split('embarc ' + cmd), cwd=cwd, stderr=stderr)
    except subprocess.CalledProcessError:
        print('cmd: embarc:', shutil.which('embarc'), file=sys.stderr)
        raise


@pytest.fixture()
def get_osp():
	runcmd(["config", "osp", "--add", "new_osp", EMBARC_OSP_URL])
	runcmd(["config", "osp", "--set", "new_osp"])
    app_path = os.path.join(getcwd(), "helloworld")
    if not os.path.exists(app_path):
        popen(["embarc", "new", "--quick"])