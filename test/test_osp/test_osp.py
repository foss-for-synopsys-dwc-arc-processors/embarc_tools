from __future__ import print_function, division
from embarc_tools.osp import osp, repo
from embarc_tools.download_manager import getcwd
from embarc_tools.settings import EMBARC_OSP_URL
from embarc_tools.notify import print_string
from embarc_tools.project import Generator
import unittest
import os
import shutil


class TestBuilder(unittest.TestCase):
    def setUp(self):
        super(TestBuilder, self).setUp()
        self.ospclass = osp.OSP()

    def test_global_osp(self):
        self.ospclass.list_path()
        config = "EMBARC_OSP_ROOT"
        if self.ospclass.get_path(str("new_osp")):
            self.ospclass.set_global(config, str("new_osp"))
        else:
            osprepo = repo.Repo.fromurl(EMBARC_OSP_URL)
            path = getcwd()
            source_type = "git"
            name = "new_osp"
            print_string("Start clone {}".format(osprepo.name))
            osprepo.clone(osprepo.url, path=os.path.join(path, name), rev=None, depth=None, protocol=None, offline=False)
            print_string("Finish clone {}".format(osprepo.name))
            self.ospclass.set_path(name, source_type, os.path.join(path, name), url)
            print_string("Add (%s) to user profile osp.json" % os.path.join(path, osprepo.name))
            self.ospclass.set_global(config, name)

    def test_rename(self):
        if self.ospclass.get_path(str("new_osp")):
            self.ospclass.rename(str("new_osp"), str("rename_osp"))

    def test_remove(self):
        if self.ospclass.get_path(str("new_osp")):
            self.ospclass.remove(str("new_osp"))

    def test_is_osp(self):
        path = self.ospclass.get_path(str("new_osp"))
        if path:
            self.ospclass.is_osp(path)

    def tearDown(self):
        self.ospclass.clear_path()
