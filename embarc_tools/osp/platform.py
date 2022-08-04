import os
import re
import pathlib
import subprocess
import xml.etree.ElementTree as ET


class Platform:

    platform_tags = {
        "bcr.dmac_build": "dma",
        "icache.present": "icache",
        "dcache.present": "dcache",
        "bcr.timer_build": "timer",
        "bcr.mpu_build": "mpu",
        "bcr.cluster_build.num_cores": "smp",
        "xy": "xymem"
    }

    def __init__(self, name, version=None, core=None):
        """Constructor.
        """
        self.name = name
        self.version = version
        self.core = core
        self.run = False

        self.type = "na"
        self.simulation = "na"
        self.peripherals = list()
        self.supported_versions = list()
        self.supported_cores = list()

        self.configs = dict()

    def _get_peripherals(self, onchip_ip_list):
        ip_list = onchip_ip_list.split()
        for ip in ip_list:
            peripheral = ip.split("/", maxsplit=1)
            if len(peripheral) == 2:
                self.peripherals.append(peripheral[1])

    def _extract_mk_vars(self, data):
        mk_vars = dict()
        mk_var_types = ["environment", "makefile", "'override'"]
        re_var = re.compile(r"^#\s*Variables\b")                # start of variable segment
        re_varend = re.compile(r"^#\s*variable")                # end of variables
        state = None                                            # state of parser
        mname = None
        for line in data.splitlines():
            try:
                line = line.decode("utf-8").strip()
            except UnicodeDecodeError:                          # GMSL has illegal sequence of characters
                continue
            if "$(" in line:                                    # command cubstitution
                continue
            if state is None and re_var.search(line):
                state = "var"
            elif state == "var":
                if re_varend.search(line):                      # last line of variable block
                    state = "end"
                    break
                if line.startswith("#"):                        # type of variable
                    var_type = line.split()
                    mname = var_type[1]
                elif mname is not None:
                    if mk_var_types is not None and mname not in mk_var_types:
                        continue
                    if mname not in mk_vars:
                        mk_vars[mname] = dict()
                    var_content = line.split(maxsplit=2)
                    if len(var_content) == 3:
                        mk_vars[mname][var_content[0]] = var_content[2]
                        if var_content[0] == "ONCHIP_IP_LIST":
                            if not self.peripherals:
                                self._get_peripherals(var_content[2])
                        if var_content[0] == "SUPPORTED_BD_VERS":
                            if not self.supported_versions:
                                self.supported_versions = var_content[2].split()
                        if var_content[0] == "SUPPORTED_CORES":
                            self.supported_cores = var_content[2].split()
                    mname = None
        self.configs.update(mk_vars)

    def get_configs(self, example, embarc_root):
        cmd = ["make", "EMBARC_ROOT=%s" % embarc_root]
        if self.name is not None:
            cmd.append("BOARD=%s" % (self.name))
        cmd.extend(["-C", example, "-pn"])
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            output = ex.output
        self._extract_mk_vars(output)
        override = self.configs.get("'override'", {})
        self.name = override.get("BOARD")
        self.version = override.get("BD_VER")
        self.core = override.get("CUR_CORE")

    def _parse_core_props(self, version, core, tcf):
        configs = dict()
        tags = list()
        with open(tcf, "rb") as f:
            tree = ET.ElementTree(ET.fromstring(f.read().decode("utf-8")))
            eleTestsuites = tree.getroot()
            core_tag = eleTestsuites.findall('configuration/[@filename="core.props"]')
            if core_tag:
                core_text = core_tag[0].find("string").text
                core_props = core_text.splitlines()
                for line in core_props:
                    if not line:
                        continue
                    key, value = line.strip('\t').split("=", maxsplit=1)
                    configs[key[12:]] = value
                    if key[12:] in self.platform_tags.keys():
                        if key[12:] == "bcr.cluster_build.num_cores":
                            if int(value) > 1:
                                tags.append("smp")
                            continue
                        tags.append(self.platform_tags[key[12:]])
        if version not in self.configs:
            self.configs[version] = dict()
        self.configs[version][core] = {
            "configs": configs,
            "tags": tags
        }

    def get_cores(self, example, version, embarc_root):
        cmd = ["make", "EMBARC_ROOT=%s" % embarc_root]
        cmd.append("BOARD=%s" % (self.name))
        cmd.append("BD_VER=%s" % (version))
        cmd.extend(["-C", example])
        cmd.append("-pn")
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            output = ex.output
        self._extract_mk_vars(output)

        board_root = os.path.join(embarc_root, "board", self.name)
        for file in pathlib.Path(board_root).glob('**/*.tcf'):
            if version in str(file):
                tcf = os.path.join(board_root, str(file))
                for core in self.supported_cores:
                    if core in tcf:
                        self._parse_core_props(version, core, tcf)
        return self.supported_cores

    def __repr__(self):
        return "<%s version %s core %s on arc>" % (self.name, self.version, self.core)
