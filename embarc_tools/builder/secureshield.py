from __future__ import print_function, unicode_literals
import os
from datetime import datetime as dt
from ..download_manager import cd, getcwd, read_json
from ..exporter import Exporter
from ..notify import print_string


CONFIG_PATH = 'secureshield_appl_config.json'
CONTAIN_CONFIG_PATH = 'container_cfg.c'
SECURESHIELD_APPL_CONFIG_PATH = 'secureshield_appl_config.h'
LINKER_NORMAL_PATH = 'linker_normal_temp.ld'
LINKER_SECURE_PATH = 'linker_secure_temp.ld'


def check_config(config):
	flag = False

	for item in config['containers']:
		if item['is_background_container'] == True:
			flag = True
			break

	if config['secureshield_version'] == 1 or config['secureshield_version'] == 2:
		flag &= True
	else:
		flag &= False

	return flag


def cal_link_section(config):
	if config['secureshield_version'] == 2:
		alignment = 'CONTAINER_ADDRESS_ALIGNMENT'
	else:
		alignment = 'CONTAINER_SIZE_ALIGNMENT(2048)'

	secure_ram_section = []
	secure_rom_section = []
	normal_ram_section = []
	normal_rom_section = []

	for item in config['containers']:
		if item['is_background_container']:
			continue

		if item['is_secure']:
			secure_ram_section.append({'section_name':item['container_name'],'alignment':alignment})
			secure_rom_section.append({'section_name':item['container_name'],'alignment':alignment})
		else:
			normal_ram_section.append({'section_name':item['container_name'],'alignment':alignment})
			normal_rom_section.append({'section_name':item['container_name'],'alignment':alignment})

	for item in config['shared_memory']:
		if item['is_secure'] == True and item['is_rom'] == True:
			secure_rom_section.append({'section_name':item['region_name'],'alignment':alignment})
		if item['is_secure'] == True and item['is_rom'] == False:
			secure_ram_section.append({'section_name':item['region_name'],'alignment':alignment})
		if item['is_secure'] == False and item['is_rom'] == True:
			normal_rom_section.append({'section_name':item['region_name'],'alignment':alignment})
		if item['is_secure'] == False and item['is_rom'] == False:
			normal_ram_section.append({'section_name':item['region_name'],'alignment':alignment})

	if len(secure_ram_section):
		config['secure_ram_section'] = secure_ram_section
	if len(secure_rom_section):
		config['secure_rom_section'] = secure_rom_section
	if len(normal_ram_section):
		config['normal_ram_section'] = normal_ram_section
	if len(normal_rom_section):
		config['normal_rom_section'] = normal_rom_section


def secureshield_appl_cfg_gen(toolchain=None, root=None):
	config = None
	if toolchain != 'gnu' and toolchain != 'mw':
		print_string("please set a valid toolchain")
		sys.exit(1)
	if os.path.exists(CONFIG_PATH):
		config = read_json(CONFIG_PATH)
	if config == None:
		return False
	elif check_config(config) == False:
		print_string("please check the application config")
		print_string("exit application configuration generator")
		return False

	config['build_year'] = str(dt.now().year)
	cal_link_section(config)
	exporter = Exporter("secureshield")
	exporter.gen_file_jinja("container_cfg.c.tmpl", config, CONTAIN_CONFIG_PATH, root)
	exporter.gen_file_jinja("secureshield_appl_config.h.tmpl", config, SECURESHIELD_APPL_CONFIG_PATH, root)
	if toolchain == 'mw':
		exporter.gen_file_jinja("secureshield_normal_mw.ld.tmpl", config, LINKER_NORMAL_PATH, root)
		exporter.gen_file_jinja("secureshield_secure_mw.ld.tmpl", config, LINKER_SECURE_PATH, root)
	else:
		exporter.gen_file_jinja("secureshield_normal_gnu.ld.tmpl", config, LINKER_NORMAL_PATH, root)
		exporter.gen_file_jinja("secureshield_secure_gnu.ld.tmpl", config, LINKER_SECURE_PATH, root)
	return True
