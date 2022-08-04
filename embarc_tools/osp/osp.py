from __future__ import print_function, division, unicode_literals
import os
import sys
import shlex
import logging
import subprocess
from pathlib import Path
from ..settings import get_input, is_embarc_base
from ..utils import read_json, generate_json


CFG_ROOT = os.path.join(os.path.expanduser("~"), ".embarc_cli")
GLOBAL_CFG_FILE = os.path.join(CFG_ROOT, "global_config.json")
OSP_CFG = os.path.join(CFG_ROOT, "osp.json")


def quote_sh_list(cmd):
    return ' '.join(shlex.quote(s) for s in cmd)


def _maybe_sha(rev):
    try:
        int(rev, 16)
    except ValueError:
        return False

    return len(rev) <= 40


class OSP(object):
    def __init__(self):
        self.root = CFG_ROOT
        self.global_cfg_file = GLOBAL_CFG_FILE
        self.osp_cfg = OSP_CFG
        self._init_cfg()

    def _init_cfg(self):
        os.makedirs(CFG_ROOT, exist_ok=True)
        if not os.path.exists(OSP_CFG):
            try:
                generate_json(dict(), OSP_CFG)
            except Exception as e:
                logging.error("Failed to create file {}, {}".format(OSP_CFG, e))
        if not os.path.exists(GLOBAL_CFG_FILE):
            try:
                global_config = dict()
                global_config["EMBARC_ROOT"] = str()
                global_config["TOOLCHAIN"] = str()
                global_config["BUILD_CONFIG"] = dict()
                global_config["BUILD_CONFIG"]["BOARD"] = str()
                global_config["BUILD_CONFIG"]["BD_VER"] = str()
                global_config["BUILD_CONFIG"]["CUR_CORE"] = str()
                generate_json(global_config, GLOBAL_CFG_FILE)
            except Exception as e:
                logging.error("Failed to create file {}, {}".format(GLOBAL_CFG_FILE, e))

    @staticmethod
    def check_call(args, cwd=None):
        subprocess.check_call(args, cwd=cwd)

    def is_osp(self, dest):
        return is_embarc_base(dest)

    def check_osp(self, path):
        if path:
            osp_root = path.replace("\\", "/")
        else:
            osp_root = path
        if not osp_root or not self.is_osp(osp_root):
            logging.warning("{} is not a valid osp root".format(osp_root))
            self.list()
            while True:
                input_root = get_input("Choose osp root or set another path as osp root: ")
                if not self.is_osp(input_root):
                    cur_osp = read_json(self.osp_cfg)
                    info = cur_osp.get(input_root, None)
                    if info:
                        select_dir = info.get("directory", None)
                        if not self.is_osp(select_dir):
                            logging.warning("{} is not a valid osp root, remove it".format(input_root))
                            self.remove(input_root)
                            continue
                        input_root = info["directory"]
                if not self.is_osp(input_root):
                    logging.warning("What you choose is not a valid osp root")
                    logging.warning("Please set a valid osp root or download embarc osp first")
                    continue

                break
            osp_root = input_root.replace("\\", "/")
        return osp_root

    def local(self, name, dest):
        if not self.is_osp(dest):
            logging.error("dest % is not a valid osp root" % (dest))
            sys.exit(1)
        if Path(dest).exists():
            local_dir = Path(dest).resolve()
            cur_osp = read_json(self.osp_cfg)
            if cur_osp.get(name, None):
                logging.error("%s already exists in %s" % (name, self.osp_cfg))
                sys.exit(1)
            else:
                cur_osp[name] = {"type": "local", "directory": str(local_dir)}
                generate_json(cur_osp, self.osp_cfg)

        else:
            logging.error("Can't find {}".format(dest))
            sys.exit(1)

    def create(self, name, url, rev, dest):
        if Path(dest).exists():
            logging.error("refusing to clone into existing location %s" % dest)
            sys.exit(1)
        dest = os.path.abspath(dest).replace("\\", "/")
        cur_osp = read_json(self.osp_cfg)
        if cur_osp.get(name, None):
            logging.error("%s already exists in %s" % (name, self.osp_cfg))
            sys.exit(1)
        try:
            self.check_call(('git', 'init', dest))
            self.check_call(('git', 'remote', 'add', 'origin', '--', url),
                            cwd=dest)
            maybe_sha = _maybe_sha(rev)
            if maybe_sha:
                self.check_call(('git', 'fetch', 'origin', '--tags',
                                '--', 'refs/heads/*:refs/remotes/origin/*'),
                                cwd=dest)
            else:
                self.check_call(('git', 'fetch', 'origin', '--tags', '--',
                                rev, 'refs/heads/*:refs/remotes/origin/*'),
                                cwd=dest)

            try:
                self.check_call(('git', 'show-ref', '--', rev), cwd=dest)
                local_rev = True
            except subprocess.CalledProcessError:
                local_rev = False

            if local_rev or maybe_sha:
                self.check_call(('git', 'checkout', rev), cwd=dest)
            else:
                self.check_call(('git', 'checkout', 'FETCH_HEAD'), cwd=dest)
        except subprocess.CalledProcessError:
            logging.error("Failed to clone osp from {}:{}".format(url, rev))
            sys.exit(1)
        cur_osp[name] = {"type": "git", "source": url, "rev": rev, "directory": dest}
        generate_json(cur_osp, self.osp_cfg)

    def remove(self, name):
        cur_osp = read_json(self.osp_cfg)
        if cur_osp.get(name, None):
            cur_osp.pop(name)
            generate_json(cur_osp, self.osp_cfg)
        else:
            logging.error("no such osp %s" % (name))
            sys.exit(1)

    def rename(self, old, new):
        cur_osp = read_json(self.osp_cfg)
        if cur_osp.get(old, None):
            cur_osp[new] = cur_osp[old]
            cur_osp.pop(old)
            generate_json(cur_osp, self.osp_cfg)
        else:
            logging.error("no such osp %s" % (old))
            sys.exit(1)

    def list(self):
        cur_osp = read_json(self.osp_cfg)
        if cur_osp:
            for name, info in cur_osp.items():
                sys.stdout.write("\n{:<5}\n {:<50}\n".format(name, info["directory"]))
                sys.stdout.flush()
            return cur_osp

    def set_global(self, name):
        cur_global = read_json(self.global_cfg_file)
        if self.is_osp(name):
            cur_global["EMBARC_ROOT"] = name
            generate_json(cur_global, self.global_cfg_file)
        else:
            cur_osp = read_json(self.osp_cfg)
            if cur_osp.get(name, None):
                cur_global["EMBARC_ROOT"] = cur_osp[name]["directory"]
                generate_json(cur_global, self.global_cfg_file)
            else:
                logging.error("no such osp %s" % (name))
                sys.exit(1)
