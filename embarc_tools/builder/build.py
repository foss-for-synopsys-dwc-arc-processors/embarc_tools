import sys
import os
import glob
import re
import random
import psutil
import signal
import logging
import time
import threading
import subprocess
from elftools.elf.elffile import ELFFile
from distutils.spawn import find_executable
from ..settings import MAKEFILENAMES, is_embarc_makefile, is_embarc_base
from ..utils import delete_dir_files, generate_json, read_json
from ..osp import platform
from ..builder import secureshield
from ..generator import Exporter


class embARC_Builder(object):
    def __init__(self, source_dir, build_dir,
                 board=None, board_version=None,
                 core=None, toolchain=None,
                 embarc_root=None,
                 buildopts=None,
                 embarc_config=None):
        self.name = None
        self.source_dir = source_dir
        self.build_dir = build_dir
        self.embarc_root = embarc_root

        self.platform = platform.Platform(board, board_version, core)
        self.toolchain = toolchain

        self.secureshield_config = None

        self.target = None

        self.extra_build_opt = buildopts

        self.cache_configs = dict()

        self.embarc_config = embarc_config
        self.log = "build.log"
        self.returncode = None
        self.terminated = False
        self.status = "na"

    def find_platform(self):
        if not self.platform.name:
            if self.cache_configs.get("BOARD", None):
                self.platform.name = self.cache_configs["BOARD"]
        if not self.platform.name:
            if not self.embarc_root:
                logging.error("unable to determine a supported board")
                sys.exit(1)
            else:
                for file in glob.glob(os.path.join(self.embarc_root, "board", "*", "*.mk")):
                    try:
                        self.platform.name = os.path.splitext(os.path.basename(file))[0]
                        break
                    except RuntimeError as e:
                        logging.error("E: failed to find a board. %s" % e)
        if not self.platform.version:
            if self.cache_configs.get("BD_VER", None):
                self.platform.version = self.cache_configs["BD_VER"]
        if not self.platform.version:
            self.platform.version = self.platform.get_versions(self.source_dir, self.embarc_root)[0]
        if not self.platform.core:
            if self.cache_configs.get("CUR_CORE", None):
                self.platform.core = self.cache_configs["CUR_CORE"]
        if not self.platform.core:
            self.platform.core = self.platform.get_cores(self.platform.version, self.source_dir, self.embarc_root)[0]
        logging.info("platform: {}".format(self.platform))
        self.cache_configs["BOARD"] = self.platform.name
        self.cache_configs["BD_VER"] = self.platform.version
        self.cache_configs["CUR_CORE"] = self.platform.core

    def check_source_dir(self):
        app_normpath = os.path.abspath(self.source_dir)
        if not os.path.isdir(app_normpath):
            logging.error(f"Cannot find folder {app_normpath}")
            sys.exit(1)
        current_makefile = None
        for makename in MAKEFILENAMES:
            if makename in os.listdir(app_normpath):
                current_makefile = os.path.join(app_normpath, makename)
                break
        if not current_makefile:
            logging.error("Cannot find makefile")
            sys.exit(1)
        else:
            is_makefile_valid, embarc_root, name = is_embarc_makefile(current_makefile)
            if not is_makefile_valid:
                logging.error("makefile {current_makefile} is invalid")
                sys.exit(1)
            else:
                self.embarc_root = os.path.abspath(os.path.join(self.source_dir, embarc_root))
                self.name = name if name else os.path.basename(app_normpath)
        self.source_dir = app_normpath

    def setup_build(self):
        logging.info("setting up build configurations ...")
        if not self.build_dir:
            logging.error("unable to determine the build folder, check the specified build directory")
            sys.exit(1)
        if os.path.exists(self.build_dir):
            if not os.path.isdir(self.build_dir):
                logging.error("build directory {} exists and is not a directory".format(self.build_dir))
                sys.exit(1)
        else:
            os.makedirs(self.build_dir, exist_ok=False)
        self.check_source_dir()
        logging.info("application: {}".format(self.source_dir.replace("\\", "/")))
        if os.path.exists(self.embarc_config):
            logging.info("get cached config from {}".format(self.embarc_config))
            self.cache_configs = read_json(self.embarc_config)
        if self.cache_configs.get("EMBARC_ROOT", None):
            if is_embarc_base(self.cache_configs["EMBARC_ROOT"]):
                self.embarc_root = self.cache_configs["EMBARC_ROOT"]
                logging.info("embARC root: {}".format(self.embarc_root))
        self.cache_configs["EMBARC_ROOT"] = self.embarc_root
        self.find_platform()
        self.toolchain = self.toolchain or self.cache_configs.get("TOOLCHAIN", None)
        if not self.toolchain:
            logging.error("unable to determine build toolchain")
            sys.exit(1)
        logging.info("toolchain: {}".format(self.toolchain))
        self.cache_configs["TOOLCHAIN"] = self.toolchain
        secureshield_config = secureshield.common_check(
            self.toolchain, self.platform.name, self.source_dir)
        if secureshield_config:
            logging.info("found secureshield configurations")
            self.secureshield_config = secureshield_config

    def terminate(self, proc):
        for child in psutil.Process(proc.pid).children(recursive=True):
            try:
                os.kill(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        proc.terminate()
        time.sleep(0.5)
        proc.kill()
        self.terminated = True

    def _output_reader(self, proc):
        log_out_fp = open(os.path.join(self.build_dir, self.log), "wt")
        for line in iter(proc.stdout.readline, b''):
            if proc.args[-1] in ["opt", "info", "all"]:
                print(line.decode('utf-8').rstrip())
            log_out_fp.write(line.decode('utf-8'))
            log_out_fp.flush()
        log_out_fp.close()

    def do_build(self, command):
        logging.info("start to build application\n")
        env = os.environ.copy()

        with subprocess.Popen(command, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, cwd=self.build_dir, env=env) as proc:
            t = threading.Thread(target=self._output_reader, args=(proc,), daemon=True)
            t.start()
            t.join()
            if t.is_alive():
                self.terminate(proc)
                t.join()
            proc.wait()
            self.returncode = proc.returncode

    def get_size(self):
        SHF_WRITE = 0x1
        SHF_ALLOC = 0x2
        SHF_EXEC = 0x4
        SHF_WRITE_ALLOC = SHF_WRITE | SHF_ALLOC
        SHF_ALLOC_EXEC = SHF_ALLOC | SHF_EXEC
        rom_addr_ranges = list()
        ram_addr_ranges = list()
        rom_size = 0
        ram_size = 0
        kernel = os.path.join(self.build_dir,
                              "obj_%s_%s" % (self.platform.name, self.platform.version),
                              "%s_%s" % (self.toolchain, self.platform.core),
                              "%s_%s_%s.elf" % (self.name, self.toolchain, self.platform.core))
        if not os.path.exists(kernel):
            logging.error("Can't find the kernel file {}".format(kernel))
            sys.exit(1)
        elf = ELFFile(open(kernel, "rb"))
        for section in elf.iter_sections():
            size = section['sh_size']
            sec_start = section['sh_addr']
            sec_end = sec_start + size - 1
            bound = {'start': sec_start, 'end': sec_end}

            if section['sh_type'] == 'SHT_NOBITS':
                # BSS and noinit sections
                ram_addr_ranges.append(bound)
                ram_size += size
            elif section['sh_type'] == 'SHT_PROGBITS':
                # Sections to be in flash or memory
                flags = section['sh_flags']
                if (flags & SHF_ALLOC_EXEC) == SHF_ALLOC_EXEC:
                    # Text section
                    rom_addr_ranges.append(bound)
                    rom_size += size
                elif (flags & SHF_WRITE_ALLOC) == SHF_WRITE_ALLOC:
                    # Data occupies both ROM and RAM
                    # since at boot, content is copied from ROM to RAM
                    rom_addr_ranges.append(bound)
                    rom_size += size

                    ram_addr_ranges.append(bound)
                    ram_size += size
                elif (flags & SHF_ALLOC) == SHF_ALLOC:
                    # Read only data
                    rom_addr_ranges.append(bound)
                    rom_size += size
        logging.info("rom total: {:<10}  ram total: {:<10}".format(rom_size, ram_size))

    def build_target(self, target):
        self.setup_build()
        make_opts = [
            "make", "BOARD=%s" % self.platform.name,
            "BD_VER=%s" % self.platform.version,
            "CUR_CORE=%s" % self.platform.core,
            "TOOLCHAIN=%s" % self.toolchain,
            "EMBARC_ROOT=%s" % self.embarc_root,
            "-C", self.source_dir,
            "OUT_DIR_ROOT=%s" % (self.build_dir)
        ]
        if self.extra_build_opt:
            make_opts.extend(self.extra_build_opt)
        self.target = target
        logging.info("build target: {}".format(target))
        if target == "clean":
            self.clean()
            return
        start_time = time.time()

        if self.secureshield_config:
            with secureshield.secureshield_appl_cfg_gen(self.toolchain, self.secureshield_config, self.source_dir):
                make_opts.append("USE_SECURESHIELD_APPL_GEN=1")
                make_opts.append(self.target)
                self.do_build(make_opts)
        else:
            make_opts.append(self.target)
            self.do_build(make_opts)
        build_time = time.time() - start_time
        sys.stdout.write("\n")
        sys.stdout.flush()
        if not self.terminated and self.returncode != 0:
            logging.error("command failed: {}".format(" ".join(make_opts)))
            self.status = "failed"
        elif self.terminated:
            logging.error("command timeout: {}".format(" ".join(make_opts)))
            self.status = "timeout"
        else:
            self.status = "passed"

        if self.status == "passed" and self.target in ["elf", "all"]:
            logging.info("command completed in: ({})s  ".format(build_time))
            self.get_size()
        if not self.embarc_config:
            self.embarc_config = os.path.join(self.build_dir, "config.json")
        generate_json(self.cache_configs, self.embarc_config)

    def generate_ide(self):
        self.setup_build()
        generator = Generator()
        for project in generator.generate_eclipse(builder=self):
            project.generate()

    def clean(self):
        target = os.path.join(self.build_dir,
                              "obj_%s_%s" % (self.platform.name, self.platform.version))
        logging.info("remove directory {}".format(target))
        delete_dir_files(target, True)

    def distclean(self, app):
        for dir in os.listdir(self.build_dir):
            target = os.path.join(self.build_dir, dir)
            if os.path.isdir(target) and dir.startswith("obj_"):
                delete_dir_files(target, True)


class Generator(object):

    def generate_eclipse(self, builder):
        yield EclipseARC(builder=builder)


class EclipseARC(object):
    def __init__(self, builder):
        self.builder = builder
        self.defines = list()
        self.includes = list()
        self.openocd_cfg = None
        self.file_types = ["cpp", "c", "s", "obj", "lib", "h", "mk"]

    def get_opt(self):
        command = [
            "make", "BOARD=%s" % (self.builder.platform.name),
            "BD_VER=%s" % (self.builder.platform.version),
            "CUR_CORE=%s" % (self.builder.platform.core),
            "TOOLCHAIN=%s" % self.builder.toolchain,
            "EMBARC_ROOT=%s" % self.builder.embarc_root,
            "-C", self.builder.source_dir,
            "opt"
        ]
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
            if output:
                lines = output.decode("utf-8").splitlines()
                for line in lines:
                    if "COMPILE_OPT" in line:
                        opts = line.split()
                        for opt in opts:
                            if opt.startswith("-D"):
                                self.defines.append(opt[2:])
                            elif opt.startswith("-I"):
                                include = opt[2:]
                                if include.startswith("obj_%s_%s" % (self.builder.platform.name, self.builder.platform.version)):
                                    include = os.path.join(self.builder.build_dir, include)
                                self.includes.append(include.replace("\\", "/"))
                            else:
                                continue
                    elif "DBG_HW_FLAGS" in line:
                        openocd = re.search(r'-s (.*) -f (.*)" ', line)
                        if openocd:
                            self.openocd_script = openocd.group(1).strip()
                            self.openocd_cfg = openocd.group(2).strip()
                        break
                    else:
                        continue

        except subprocess.CalledProcessError as ex:
            logging.error("Fail to run command {}".format(command))
            sys.exit(ex.output.decode("utf-8"))

    def get_cproject_cfg(self):
        make_opts = [
            "BOARD=%s" % self.builder.platform.name,
            "BD_VER=%s" % self.builder.platform.version,
            "CUR_CORE=%s" % self.builder.platform.core,
            "TOOLCHAIN=%s" % self.builder.toolchain,
            "EMBARC_ROOT=%s" % self.builder.embarc_root.replace("\\", "/"),
            "-C", self.builder.source_dir.replace("\\", "/"),
            "OUT_DIR_ROOT=%s" % (self.builder.build_dir.replace("\\", "/")),
        ]
        cproject_cfg = {
            "name": self.builder.name,
            "core": {
                self.builder.platform.core: {
                    "description": str(self.builder.platform)[1:-1].upper(),
                    "id": random.randint(1000000000, 2000000000)
                }
            },
            "includes": [],
            "defines": self.defines,
            "make_opts": " ".join(make_opts),
            "toolchain": self.builder.toolchain,
        }
        return cproject_cfg

    def get_debug_cfg(self):
        debug_cfg = dict()
        debug_cfg["name"] = self.builder.name
        nsimdrv = find_executable("nsimdrv")
        if not nsimdrv:
            logging.error("can not find nsim")
            sys.exit(1)
        debug_cfg["nsim"] = nsimdrv
        debug_cfg["nsim_tcf"] = os.path.join(self.builder.embarc_root,
                                             "board/nsim/configs/%s" % self.builder.platform.version,
                                             "tcf/%s.tcf" % self.builder.platform.core).replace("\\", "/")
        debug_cfg["nsim_port"] = 49105
        gnu_executable = find_executable("arc-elf32-gcc")
        if not gnu_executable:
            logging.error("can not find arc-elf32-gcc")
            sys.exit(1)
        debug_cfg["openocd_bin"] = os.path.join(os.path.dirname(gnu_executable),
                                                "openocd.exe").replace("\\", "/")
        debug_cfg["openocd_cfg"] = self.openocd_cfg.replace("\\", "/")
        return debug_cfg

    def generate(self):
        self.get_opt()
        project_cfg = dict()
        project_cfg["links"] = dict()
        project_cfg["name"] = self.builder.name
        embarc_root = self.builder.embarc_root.replace("\\", "/")
        build_dir = self.builder.build_dir.replace("\\", "/")
        source_dir = self.builder.source_dir.replace("\\", "/")
        project_cfg["embarc_root"] = embarc_root

        project_cfg["sources"] = dict()
        for root, _, files in os.walk(source_dir, topdown=False):
            root = root.replace("\\", "/")
            if not root.startswith(build_dir):
                virtual_dir = root.replace(source_dir, "application")
                project_cfg["sources"][virtual_dir] = list()
                for f in files:
                    project_cfg["sources"][virtual_dir].append(
                        {"name": f, "dir": root}
                    )

        cproject_cfg_include = set()

        for include in self.includes:
            if include == embarc_root:
                continue
            if "embARC_generated" in include:
                virtual_dir = include.replace(build_dir, "")
                cproject_cfg_include.add(virtual_dir)
                continue
            if include == ".":
                cproject_cfg_include.add("")
                continue
            for file in os.listdir(include):
                virtual_dir = include.replace(embarc_root, "embARC")
                cproject_cfg_include.add(virtual_dir)
                if os.path.isfile(os.path.join(include, file)):
                    if os.path.splitext(file)[-1][1:] in self.file_types or (file in MAKEFILENAMES):
                        if not project_cfg["links"].get(virtual_dir, None):
                            project_cfg["links"][virtual_dir] = list()
                        link = {"name": file,
                                "dir": include.replace(embarc_root, "OSP_ROOT")}
                        if link not in project_cfg["links"][virtual_dir]:
                            project_cfg["links"][virtual_dir].append(
                                {"name": file,
                                 "dir": include.replace(embarc_root, "OSP_ROOT")}
                            )

        exporter = Exporter(self.builder.toolchain)
        logging.info("generating esclipse project description file ...")
        exporter.gen_file_jinja(
            "project.tmpl", project_cfg, ".project", build_dir
        )

        cproject_cfg = self.get_cproject_cfg()
        cproject_cfg["includes"] = list(cproject_cfg_include)
        logging.info("generating esclipse cdt into .cproject file ...")
        exporter.gen_file_jinja(
            ".cproject.tmpl", cproject_cfg, ".cproject", build_dir
        )

        debug_cfg = self.get_debug_cfg()
        debug_cfg["core"] = cproject_cfg["core"]
        debug_cfg["board"] = self.builder.platform.name
        debug_cfg["bd_ver"] = self.builder.platform.version
        logging.info("generating esclipse launch configuration file ...")
        exporter.gen_file_jinja(
            ".launch.tmpl", debug_cfg, "%s-%s.launch" % (debug_cfg["name"], self.builder.platform.core), build_dir
        )
        logging.info(
            "open Eclipse - >File >Open Projects from File System >Paste\n{}".format(
                build_dir
            )
        )
