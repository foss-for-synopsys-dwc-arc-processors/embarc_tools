import os
import sys
import unittest
from unittest import defaultTestLoader
import HTMLTestRunner
import coverage
from embarc_tools.osp import repo, osp
from embarc_tools.download_manager import getcwd
from embarc_tools.toolchain import gnu
from embarc_tools.settings import EMBARC_OSP_URL
from embarc_tools.notify import print_string


def get_allcase(case_path):
    discover = unittest.defaultTestLoader.discover(case_path, pattern="test*.py")
    return discover

def before_install():
    ospclass = osp.OSP()
    url = EMBARC_OSP_URL
    osprepo = repo.Repo.fromurl(url)
    path = getcwd()
    source_type = "git"
    name = "new_osp"
    if not os.path.exists(name):
        print_string("Start clone {}".format(osprepo.name))
        osprepo.clone(osprepo.url, path=os.path.join(path, name), rev=None, depth=None, protocol=None, offline=False)
        print_string("Finish clone {}".format(osprepo.name))
        ospclass.set_path(name, source_type, os.path.join(path, name), url)
        print_string("Add (%s) to user profile osp.json" % os.path.join(path, osprepo.name))
    if ospclass.get_path(str("new_osp")):
        config = "EMBARC_OSP_ROOT"
        ospclass.set_global(config, str("new_osp"))

def main():
    test_dir = os.path.dirname(__file__)
    embarc_tools_dir = os.path.join(os.path.abspath(os.path.dirname(test_dir)), "embarc_tools", "*")
    # include = os.path.join(include,"*")
    print(embarc_tools_dir)
    COV = coverage.coverage(branch=True, include=embarc_tools_dir)
    COV.start()
    before_install()
    pythonversion = os.environ.get("TRAVIS_PYTHON_VERSION")
    testfilepath = pythonversion + "index.html"
    ftp = open(testfilepath, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=ftp, verbosity=2, title=pythonversion)
    runner.run(get_allcase(test_dir))
    ftp.close()
    COV.stop()
    COV.save()
    print('Coverage Summary:')
    COV.report()
    basedir = os.path.abspath(test_dir)
    covdir = os.path.join(basedir, 'coverage')
    COV.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    COV.erase()

if __name__ == '__main__':
    main()
