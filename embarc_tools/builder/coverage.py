from __future__ import print_function, unicode_literals
import os
import io
import random
import time
from distutils.spawn import find_executable
from bs4 import BeautifulSoup
import serial
import subprocess
import threading
import psutil
from dateutil.parser import parse
from ..utils import delete_dir_files, processcall, getcwd, cd, mkdir, remove
from ..exporter import Exporter


def generate_gcov_report(root, app_path, obj_path, output):
    gcov_cmd = None
    if find_executable("arc-elf32-gcov"):
        gcov_cmd = "arc-elf32-gcov"
        cmd = ["gcovr", "--gcov-executable", gcov_cmd]
        cmd.extend(["-r", root])
        cmd.extend(["--object-directory", obj_path])
        cmd.extend(["--html", "--html-details",
                    "-o", output])
        processcall(cmd, stderr=subprocess.PIPE)
    else:
        print("Please install arc-elf32-gcov")


def generate_gdb_command(root, board, build_path):
    openocd = None
    object_file = None
    gnu_exec_path = find_executable("arc-elf32-gcc")
    openocd_cfg = None
    if gnu_exec_path and board != "nsim":
        gnu_root = os.path.dirname(gnu_exec_path)
        openocd = os.path.join(
            os.path.dirname(gnu_root),
            "share",
            "openocd",
            "scripts"
        )
        if board == "iotdk" or board == "emsdp":
            board_root = os.path.join(
                root,
                "board",
                board
            )
            board_cfg = "snps_" + board + ".cfg"
            for cur_root, _, files in os.walk(board_root):
                if board_cfg in files:
                    openocd_cfg = os.path.join(
                        cur_root,
                        board_cfg
                    )
        else:
            if board == "emsk":
                board_cfg = "snps_em_sk.cfg"
            elif board == "axs":
                board_cfg = "snps_axs103_hs36.cfg"
            elif board == "hsdk":
                board_cfg = "snps_hsdk.cfg"
            else:
                board_cfg = None
            if board_cfg:
                cfg_root = os.path.join(
                    openocd,
                    "board"
                )
                if board_cfg in cfg_root:
                    openocd_cfg = os.path.join(
                        cfg_root,
                        board_cfg
                    )
    for cur_root, _, files in os.walk(build_path):
        for file in files:
            if os.path.splitext(file)[-1] == ".elf":
                object_file = os.path.join(
                    cur_root,
                    file
                )
                break

    exporter = Exporter("coverage")
    config = {"board": board}
    config["object_file"] = object_file.replace("\\", "/")
    if board != "nsim":
        config = {"openocd": openocd.replace("\\", "/")}
        config = {"openocd_cfg": openocd_cfg.replace("\\", "/")}

    exporter.gen_file_jinja(
        "coverage.gdb.tmpl",
        config,
        "coverage.gdb",
        getcwd()
    )


def get_gcov_data(report):
    data = list()
    with open(report, "r") as f:
        content = f.read()
        content_bf = BeautifulSoup(content, "html.parser")
        items = content_bf.find_all("table")
        summary_bf = BeautifulSoup(str(items[0]), "html.parser")
        td_items = summary_bf.find_all("td")
        for td_item in td_items:
            if td_item.get("class"):
                key = td_item.get("class")[0]
                value = td_item.text
                item = {key: value}
                data.append(item)
        detail = list()
        detail_report_files = list()
        center_content = content_bf.find_all("center")[0]
        tr_contents = center_content.findAll('tr')
        for tr in tr_contents:
            if "href=" in str(tr):
                href = tr.findAll('a', href=True)[0]
                html_name = href['href']
                href['href'] = "#" + html_name
                detail.append(str(tr).replace(u'\xa0', u''))  # Some code is not ASCII, (e.g., options/gmsl/__gmsl)
                with open(os.path.join("coverage", html_name), "r") as key_f:
                    detail_content = key_f.read()
                    detail_bf = BeautifulSoup(detail_content, "html.parser")
                    cov_detail = detail_bf.findAll('table', attrs={'cellspacing': '0', 'cellpadding': '1'})[0]
                    if cov_detail:
                        detail_report_files.append(
                            {"name": html_name, "detail": str(cov_detail).replace(u'\xa0', u'')}
                        )
        data.append({"detail": detail})
        data.append({"files": detail_report_files})
    return data


def generate_sum_report(root, app_path, obj_path):
    result = dict()
    headName = None
    try:
        mkdir("coverage")
        with cd("coverage"):
            generate_gcov_report(root, app_path, obj_path, "coverage_sum.html")
            generate_gcov_report(app_path, app_path, obj_path, "main.html")
        osp_data = get_gcov_data("coverage/coverage_sum.html")
        main_data = get_gcov_data("coverage/main.html")

        for i in range(len(osp_data)):
            osp_data_item = osp_data[i]
            main_data_item = main_data[i]
            for key, value in osp_data_item.items():
                if key == "detail":
                    result["detail"] = value + main_data_item[key]
                if key == "files":
                    result["files"] = value + main_data_item[key]
                if "headerName" in key:
                    headName = value
                    continue
                if headName in ["Date:", "Lines:", "Branches:"]:
                    if "Date" in headName and \
                            result.get("Date", None) is None:
                        if "headerValue" in key:
                            try:
                                parse(value)
                                result["Date"] = value
                                continue
                            except Exception as e:
                                print("Sting is not a date {}".format(e))
                    if "Lines" in headName and \
                            result.get("LineExec", None) is None:
                        if "headerTableEntry" in key:
                            result["LineExec"] = int(value) + int(main_data_item[key])
                            continue
                    if "Lines" in headName and \
                            result.get("LineTotal", None) is None:
                        if "headerTableEntry" in key:
                            result["LineTotal"] = int(value) + int(main_data_item[key])
                            result["LineCoverage"] = float(result["LineExec"] * 100 / result["LineTotal"])
                            continue
                    if "Branches" in headName and \
                            result.get("BrancheExec", None) is None:
                        if "headerTableEntry" in key:
                            result["BrancheExec"] = int(value) + int(main_data_item[key])
                            continue
                    if "Branches" in headName and \
                            result.get("BrancheTotal", None) is None:
                        if "headerTableEntry" in key:
                            result["BrancheTotal"] = int(value) + int(main_data_item[key])
                            result["BrancheCoverage"] = float(result["BrancheExec"] * 100 / result["BrancheTotal"])
                            continue
                else:
                    continue
        exporter = Exporter("coverage")
        exporter.gen_file_jinja(
            "gcov.html.tmpl",
            result,
            "gcov.html",
            getcwd(),
        )
    finally:
        delete_dir_files("coverage", dir=True)


def monitor_serial(ser, stdout):
    while 1:
        s = str(stdout.readline().decode("utf-8"))
        print(s, end="")
        if "Breakpoint" in s:
            break
    print("Start monitor serial ...")
    while ser.isOpen():
        serial_line = None
        try:
            serial_line = ser.readline()
        except TypeError:
            pass
        except serial.serialutil.SerialException:
            ser.close()
            break
        if serial_line:
            sl = serial_line.decode('utf-8', 'ignore')
            print(sl, end="")
            if "GCOV_COVERAGE_DUMP_END" in sl:
                ser.close()
                break


def cmd_output_callback(proc, command):
    while True:
        s = str(proc.stdout.readline().decode("utf-8"))
        print(s, end="")
        if "nsimdrv -gdb" in s:
            break
    time.sleep(5)
    file_num = random.randint(100000, 200000)
    file_name = "gdb_message" + str(file_num) + ".log"
    with io.open(file_name, "wb") as writer, io.open(file_name, "rb", 1) as reader:
        gdb_proc = subprocess.Popen(
            command, stdout=writer, stderr=writer, shell=True, bufsize=1
        )
        end = ""
        print("[embARC] Start gdb ...")
        while True:
            decodeline = reader.read().decode()
            if decodeline == str() and gdb_proc.poll() is not None:
                break
            if decodeline != str():
                print(decodeline, end=end)
                if "Breakpoint" in decodeline:
                    break
        while True:
            s = str(proc.stdout.readline().decode("utf-8"))
            print(s, end="")
            if "GCOV_COVERAGE_DUMP_END" in s:
                try:
                    gdb_proc.wait(timeout=0.1)
                except subprocess.TimeoutExpired:
                    gdb_proc.terminate()
                try:
                    proc.wait(timeout=0.1)
                except subprocess.TimeoutExpired:
                    proc.terminate()
                break
    try:
        for cur_proc in psutil.process_iter():
            if cur_proc.name().startswith("arc-elf32-gdb"):
                cur_proc.kill()
    except Exception as e:
        print("[embARC] Failed to kill process arc-elf32-gdb {}".format(e))
    finally:
        if os.path.exists(file_name):
            remove(file_name)


def run(app_path, buildopts, outdir=None, serial_device=None):
    command = None
    relative_object_directory = "obj_{}_{}/{}_{}".format(
        buildopts["BOARD"],
        buildopts["BD_VER"],
        buildopts["TOOLCHAIN"],
        buildopts["CUR_CORE"]
    )
    object_directory = os.path.join(app_path, relative_object_directory).replace("\\", "/")
    with cd(app_path):
        if outdir is None:
            outdir = app_path
        print("[embARC] Generate gdb file ...")
        generate_gdb_command(buildopts["EMBARC_ROOT"], buildopts["BOARD"], object_directory)

        if os.path.exists("coverage.gdb"):
            if find_executable("arc-elf32-gdb"):
                command = ["arc-elf32-gdb"]
                command.extend([
                    "-x",
                    "coverage.gdb"
                ])
                if buildopts["BOARD"] == "nsim":
                    if find_executable("nsimdrv"):
                        nsim_server_cmd = ["make"]
                        buildopts_list = [
                            "%s=%s" % (key, value) for key, value in buildopts.items()
                        ]
                        nsim_server_cmd.extend(buildopts_list)
                        nsim_server_cmd.append("nsim")
                        print("[embARC] Start nsim server ...")
                        with subprocess.Popen(
                            nsim_server_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        ) as nsim_server_proc:
                            t = threading.Thread(
                                target=cmd_output_callback,
                                args=(nsim_server_proc, command)
                            )
                            t.start()
                            t.join(1000)
                            if t.is_alive():
                                t.join()
                                nsim_server_proc.terminate()
                            nsim_server_proc.wait()
                            nsim_server_proc.returncode

                else:
                    with subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    ) as proc:
                        ser = serial.Serial(
                            serial_device,
                            baudrate=115200,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS,
                            timeout=0.5
                        )
                        ser.flush()
                        t = threading.Thread(
                            target=monitor_serial,
                            daemon=True,
                            args=(ser, proc.stdout)
                        )
                        t.start()
                        t.join(1000)
                        if t.is_alive():
                            proc.terminate()
                            t.join()
                        proc.terminate()
                        proc.wait()
                        proc.returncode

                generate_sum_report(
                    buildopts["EMBARC_ROOT"],
                    app_path,
                    object_directory
                )
