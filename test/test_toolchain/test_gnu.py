from __future__ import print_function, division

import unittest
import os
import shutil
from embarc_tools.toolchain import gnu, metaware, ARCtoolchain
from embarc_tools.download_manager import delete_dir_files
from embarc_tools.settings import CURRENT_PLATFORM


class TestToolchain(unittest.TestCase):
    def setUp(self):
        super(TestToolchain, self).setUp()
        self.gnu = gnu.Gnu()
        self.mw = metaware.Mw()
        self.pack = os.path.join(os.getcwd(), "arc_gnu_2018.09_prebuilt_elf32_le_linux_install.tar.gz")

    def test_is_support(self):
        result = ARCtoolchain.is_supported("gnu")
        self.assertTrue(result)
        result = ARCtoolchain.is_supported("mw")
        self.assertTrue(result)

    def test_get_platform(self):
        result = ARCtoolchain.get_platform()
        self.assertIn(result, ["Windows", "Linux"])

    def test_check_version(self):
        gnuversion = self.gnu.check_version()
        print(gnuversion)
        mwversion = self.mw.check_version()
        print(mwversion)

    def test_download(self):
        gnu_tgz_path = self.gnu.download(version="2018.09")
        print("download ", gnu_tgz_path)
        print(os.listdir("."))
        # self.assertIsNotNone(gnu_tgz_path)

    def test_extract_file(self):
        pack = "arc_gnu_2018.09_prebuilt_elf32_le_linux_install.tar.gz"
        path = self.gnu.extract_file(self.pack)
        print("gnu pack path: ", path)

    def test_set_toolchain_env(self):
        current_platform = ARCtoolchain.get_platform()
        platform = CURRENT_PLATFORM
        if platform == "Windows":
            from embarc_tools.toolchain import windows_env_set_arc
            env_obj = windows_env_set_arc.Win32Environment(scope="user")
            # windows_env_set_arc.set_env_path(env_obj, 'Path', toolchain_root)
            # return True
        elif platform == "Linux":
            try:
                bashrc = os.path.join(os.path.expanduser("~"), '.bashrc')
                content = list()
                with open(bashrc) as f:
                    lines = f.read().splitlines()
                    print(lines)
            except Exception as e:
                print(e)
        # self.gnu.set_toolchain_env("")

    def tearDown(self):
        delete_dir_files(self.pack)
        delete_dir_files("2018.09", dir=True)
