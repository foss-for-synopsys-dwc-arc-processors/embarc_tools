import sys
import re
import subprocess
import logging


class Platform:
    def __init__(self, name, version=None, core=None):
        """Constructor.
        """
        self.name = name
        self.version = version
        self.core = core
        self.run = False
        self.openocd_cfg = None

        self.type = "na"
        self.simulation = "na"

    def get_versions(self, source_dir, embarc_root=None):
        result = list()
        cmd = ["make"]
        cmd.append("BOARD=%s" % (self.name))
        if embarc_root:
            cmd.append("EMBARC_ROOT=%s" % embarc_root)
        cmd.extend(["-C", source_dir])
        cmd.append("spopt")
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            if output:
                opt_lines = output.decode("utf-8").splitlines()
                for opt_line in opt_lines:
                    if opt_line.startswith("SUPPORTED_BD_VERS"):
                        platform_versions = opt_line.split(":", 1)[1]
                        result.extend(platform_versions.split())
                        break
        except subprocess.CalledProcessError as ex:
            pattern = re.compile(r"BOARD %s Version - (.*) are supported" % self.name)
            for line in ex.output.decode("utf-8").splitlines():
                if pattern.search(line):
                    result = re.findall(r"\d+", line)
                    break
            if not result:
                logging.error("Fail to run command {}".format(cmd))
                sys.exit(ex.output.decode("utf-8"))

        return result

    def get_cores(self, version, source_dir, embarc_root=None):
        result = list()
        cmd = ["make"]
        cmd.append("BOARD=%s" % (self.name))
        cmd.append("BD_VER=%s" % (version))
        if embarc_root:
            cmd.append("EMBARC_ROOT=%s" % embarc_root)
        cmd.extend(["-C", source_dir])
        cmd.append("spopt")
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            if output:
                opt_lines = output.decode("utf-8").splitlines()
                for opt_line in opt_lines:
                    if opt_line.startswith("SUPPORTED_CORES"):
                        platforms_cores = opt_line.split(":", 1)[1]
                        result.extend(platforms_cores.split())
                        break
        except subprocess.CalledProcessError as ex:
            pattern = re.compile(r"BOARD %s-%s Core Configurations - (.*) are supported" % (self.name, version))
            for line in ex.output.decode("utf-8").splitlines():
                searchObj = pattern.search(line)
                if searchObj:
                    result = searchObj.group(1).split()
                    break
            if not result:
                logging.error("Fail to run command {}".format(cmd))
                sys.exit(ex.output.decode("utf-8"))
        return result

    def __repr__(self):
        return "<%s version %s core %s on arc>" % (self.name, self.version, self.core)
