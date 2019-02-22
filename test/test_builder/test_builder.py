from __future__ import print_function, division
from embarc_tools.builder import build
from embarc_tools.osp import osp, repo
import unittest
import os, shutil

class TestBuilder(unittest.TestCase):
    def setUp(self):
        super(TestBuilder, self).setUp()
        ospclass = osp.OSP()
        ospclass.list_path()
        self.osp_root = ospclass.get_path("new_osp")
        if not self.osp_root:
            url = "https://github.com/foss-for-synopsys-dwc-arc-processors/embarc_osp"
            osprepo = repo.Repo.fromurl(url)
            path = os.getcwd()
            if not os.path.exists(osprepo.name):
                osprepo.clone(osprepo.url, path=os.path.join(path, osprepo.name), rev=None, depth=None, protocol=None, offline=False)
                ospclass.set_path(os.path.join(path, osprepo.name), osprepo.url)
            self.osp_root = os.path.join(path, osprepo.name)
        self.app_path = os.path.join(self.osp_root, "example/baremetal/blinky")
        self.buildopts = {"BOARD":"emsk", "BD_VER":"11","CUR_CORE":"arcem6","TOOLCHAIN":"gnu"}
        self.app_builder = build.embARC_Builder(osproot=self.osp_root, buildopts=self.buildopts)

    def test_build_common_check(self):
        app_path = self.app_path
        app_realpath, build_status = self.app_builder.build_common_check(app_path)
        print(build_status )
        self.assertTrue(build_status["result"])

    def test_build_target(self):
        app_path = self.app_path
        build_status = self.app_builder.build_target(app_path, target='size')
        self.app_builder.clean(app_path)


    def test_get_build_info(self):
        app_path = self.app_path
        print(self.app_builder.get_build_info(app_path))
        self.app_builder.clean(app_path)

    def test_build_elf(self):
        app_path = self.app_path
        build_status = self.app_builder.build_elf(app_path, pre_clean=False, post_clean=False)
        print(build_status['build_cmd'])
        print(build_status['time_cost'])
        print(build_status['build_msg'])

        self.app_builder.distclean(self.app_path)

    def test_build_bin_hex(self):
        app_path = self.app_path
        build_status = self.app_builder.build_bin(app_path, pre_clean=False, post_clean=False)
        print(build_status)

        build_status = self.app_builder.build_hex(app_path, pre_clean=False, post_clean=False)
        print(build_status)

        self.app_builder.distclean(self.app_path)

    def test_get_build_size(self):
        app_path = self.app_path
        build_status = self.app_builder.get_build_size(app_path)
        print(build_status)

        self.app_builder.distclean(self.app_path)



    '''def test_build_target_coverity(self):
        app_path = "C:\\Users\\jingru\\Documents\\embarc_tool\\embarc_tool\\test\\testapp"
        build_status = self.app_builder.build_target(app_path,target='all',coverity=True)
        self.app_builder.build_coverity_result()
        self.assertTrue(build_status["result"])
        app_builder.distclean(self.app_path)'''


    def tearDown(self):
        print("test builder")
