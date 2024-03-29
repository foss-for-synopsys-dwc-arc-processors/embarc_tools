from __future__ import print_function, division, unicode_literals
try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request
    from urllib2 import urlopen
    from urllib2 import URLError
import re
import os
import sys
import logging
import subprocess
from bs4 import BeautifulSoup
from distutils.spawn import find_executable
from ..toolchain import ARCtoolchain
from ..utils import download_file, extract_file, getcwd, mkdir, delete_dir_files


class Gnu(ARCtoolchain):
    '''
    version: default version is 2017.09
    root_url: from this url to down load gnu
    pack: where the gnu archive is
    executable_name: a command will be used when check gnu
    '''
    root_url = "https://github.com/foss-for-synopsys-dwc-arc-processors/toolchain/releases"
    pack = None
    path = None
    executable_name = "arc-elf32-gcc"

    def __init__(self):

        self.exe = find_executable(self.executable_name)
        if self.exe:
            self.path = os.path.split(self.exe)[0]
            self.version = self.check_version()

    @staticmethod
    def check_version():
        '''run command "arc-elf32-gcc --version" and return current gnu version'''
        cmd = ["arc-elf32-gcc", "--version"]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            if output is None:
                logging.waring("can not execute {}".format(cmd[0]))
                return None
            version = re.search(r"[0-9]*\.[0-9]*", output.decode("utf-8")).group(0)
            if version:
                return version
        except subprocess.CalledProcessError as ex:
            logging.error("Fail to run command {}".format(cmd))
            sys.exit(ex.output.decode("utf-8"))

    def _set_version(self):
        '''get current gnu version and set the self.version'''
        version = self.check_version()
        if version:
            self.version = version

    def download(self, version=None, path=None):
        '''
        version - gnu version
        path - where the gnu package will be stored
        download gnu package and return the package path
        '''
        url = None
        pack_tgz = None
        if version:
            url = self.root_url + "/download/arc-" + version + "-release/arc_gnu_" + version + "_prebuilt_elf32_le_linux_install.tar.gz"
            pack_tgz = "arc_gnu_" + version + "_prebuilt_elf32_le_linux_install.tar.gz"
        else:
            url = "https://github.com" + self._lastest_url()
            version = re.search(r"[0-9]*\.[0-9]*", url).group(0)
            pack_tgz = url.rsplit("/", 1)[1]

        if path is None:
            path = getcwd()
        gnu_tgz_path = os.path.join(path, pack_tgz)
        if not os.path.exists(path):
            mkdir(path)
        if pack_tgz in os.listdir(path):
            logging.info("GNU tgz already exists")
        else:
            logging.info("Download from (%s)" % url)
            result = download_file(url, gnu_tgz_path)
            if not result:
                logging.error("Download gnu failed")
                sys.exit(1)
        self.pack = gnu_tgz_path
        return gnu_tgz_path

    def extract_file(self, pack=None, path=None):
        '''extract gnu file from pack to path;
        pack - the path of the compressed package
        path - the compressed package is extracted to this path
        return the root path of gnu and set self.path'''
        if pack is None:
            pack = self.pack
        if path is None:
            path = getcwd()
        if pack is None:
            logging.warning("Please download gnu file first")
            return False

        else:
            version = re.search(r"[0-9]*\.[0-9]*", pack).group(0)
            if version in os.listdir(path):
                delete_dir_files(version, True)
            try:
                gnu_file_path = extract_file(pack, path)
                return gnu_file_path
            except Exception as e:
                print(e)

    def set_env(self, path=None):
        '''set environment'''
        self.set_toolchain_env("gnu", path)

    def _lastest_url(self):
        pack_format = "_ide_win_install.exe" if self.get_platform() == "Windows" else "_prebuilt_elf32_le_linux_install.tar.gz"
        try:
            request = Request(self.root_url)
            response = urlopen(request)
            content = response.read().decode('utf-8')

            div_bf = BeautifulSoup(content, features="html.parser")
            items = div_bf.find_all('div', class_='Box Box--condensed mt-3')
            latesturl = None
            if items:
                a_bf = BeautifulSoup(str(items[0]), features="html.parser")
                a_items = a_bf.find_all('a', class_='d-flex flex-items-center min-width-0')
                for a_item in a_items:
                    a_url = a_item.get('href')
                    if pack_format in a_url:
                        latesturl = str(a_url)
                        break
                return latesturl
        except URLError as e:
            if hasattr(e, "code"):
                logging.warning(e)
            if hasattr(e, "reason"):
                logging.warning(e.reason)
        else:
            logging.warning("Can not get latest veriosn Gnu")
