from __future__ import print_function, division
from embarc_tools.builder import build
from embarc_tools.osp import osp, repo
from embarc_tools.utils import popen
from embarc_tools.download_manager import getcwd, read_json
from embarc_tools.settings import EMBARC_OSP_URL, CURRENT_PLATFORM
from embarc_tools.notify import print_string
from embarc_tools.project import Generator
import unittest
import os
import shutil


class TestBuilder(unittest.TestCase):
    def setUp(self):
        super(TestBuilder, self).setUp()
        ospclass = osp.OSP()
        ospclass.list_path()
        if ospclass.get_path(str("new_osp")):
            config = "EMBARC_OSP_ROOT"
            ospclass.set_global(config, str("new_osp"))
        self.osp_root = ospclass.get_path("new_osp")
        self.app_path = os.path.join(self.osp_root, "example/baremetal/blinky")
        self.buildopts = {"BOARD": "emsk", "BD_VER": "11", "CUR_CORE": "arcem6", "TOOLCHAIN": "gnu"}
        self.app_builder = build.embARC_Builder(osproot=self.osp_root, buildopts=self.buildopts)

    def test_build_common_check(self):
        app_path = self.app_path
        app_realpath, build_status = self.app_builder.build_common_check(app_path)
        print(build_status)
        self.assertTrue(build_status["result"])

    def test_build_target(self):
        build_status = self.app_builder.build_target(self.app_path, target='size')
        embarc_config = os.path.join(self.app_path, "embarc_app.json")
        if CURRENT_PLATFORM == "Windows":
            self.app_builder.get_build_cmd(self.app_path, target=None, parallel=parallel, silent=False)
            with cd(app_path):
                generator = Generator()
                recordBuildConfig = read_json(embarc_config)
                for project in generator.generate(buildopts=recordBuildConfig):
                    project.generate()

            self.assertTrue(os.path.exists(os.path.join(self.app_path, file1)))
            self.assertTrue(os.path.exists(os.path.join(self.app_path,file2)))
        self.app_builder.clean(self.app_path)

    def test_get_build_info(self):
        app_path = self.app_path
        embarc_config = os.path.join(app_path, "embarc_app.json")
        print(self.app_builder.get_build_info(app_path))
        recordBuildConfig = read_json(embarc_config)
        print(recordBuildConfig)
        self.app_builder.clean(app_path)

    def test_build_elf(self):
        app_path = self.app_path
        build_status = self.app_builder.build_elf(app_path, pre_clean=False, post_clean=False)
        print(build_status)
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

    def tearDown(self):
        print("test builder")
