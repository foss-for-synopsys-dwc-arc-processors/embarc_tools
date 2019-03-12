from __future__ import print_function, unicode_literals
from functools import reduce
import random
import time
import io
import sys
import operator
import subprocess
import errno
import os
import yaml
from .download_manager import getcwd


def uniqify(_list):
    return reduce(lambda r, v: v in r[1] and r or (r[0].append(v) or r[1].add(v)) or r, _list, ([], set()))[0]


def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


def load_yaml_records(yaml_files):
    dictionaries = []
    for yaml_file in yaml_files:
        try:
            f = open(yaml_file, 'rt')
            dictionaries.append(yaml.load(f))
        except IOError:
            raise IOError("The file %s referenced in main yaml doesn't exist." % yaml_file)
    return dictionaries


def merge_recursive(*args):
    if all(isinstance(x, dict) for x in args):
        output = {}
        keys = reduce(operator.or_, [set(x) for x in args])

        for key in keys:
            # merge all of the ones that have them
            output[key] = merge_recursive(*[x[key] for x in args if key in x])

        return output
    return reduce(operator.add, args)


class ProcessException(Exception):
    pass


def popen(command, **kwargs):
    proc = None
    try:
        proc = subprocess.Popen(command, **kwargs)
    except OSError as e:
        if e.args[0] == errno.ENOENT:
            print(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (command[0], command[0]), e.args[0])
        else:
            raise e

    if proc and proc.wait() != 0:
        raise ProcessException(proc.returncode, command[0], ' '.join(command), getcwd())


def processcall(command, **kwargs):
    returncode = 0
    try:
        returncode = subprocess.call(command, **kwargs)
    except OSError as e:
        if e.args[0] == errno.ENOENT:
            print(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (command[0], command[0]), e.args[0])
        else:
            raise e
    return returncode


def pquery(command, output_callback=None, stdin=None, **kwargs):
    proc = None
    try:
        proc = subprocess.Popen(command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    except OSError as e:
        if e.args[0] == errno.ENOENT:
            print(
                "Could not execute \"%s\" in \"%s\".\n"
                "You can verify that it's installed and accessible from your current path by executing \"%s\".\n" % (' '.join(command), getcwd(), command[0]), e.args[0])
        else:
            raise e

    if output_callback:
        line = ""
        while 1:
            s = str(proc.stderr.read(1))
            line += s
            if s == '\r' or s == '\n':
                output_callback(line, s)
                line = ""

            if proc.returncode is None:
                proc.poll()
            else:
                break

    stdout, _ = proc.communicate(stdin)
    if proc.returncode != 0:
        print("[embARC] Run command {} return code:{} ".format(' '.join(command), proc.returncode))

    return stdout.decode("utf-8")


def pqueryOutputinline(command, console=False, **kwargs):
    proc = None
    build_out = list()
    file_num = random.randint(100000, 200000)
    file_name = "message" + str(file_num) + ".log"
    try:
        with io.open(file_name, "wb") as writer, io.open(file_name, "rb", 1) as reader:
            proc = subprocess.Popen(
                command, stdout=writer, stderr=subprocess.PIPE, shell=True, bufsize=1, **kwargs
            )
            end = ""
            # if PYTHON_VERSION.startswith("3"):
            #    end = "\n"
            try:
                while True:
                    decodeline = reader.read().decode()
                    if decodeline == str() and proc.poll() is not None:
                        break
                    if decodeline != str():
                        build_out.append(decodeline)
                        if console:
                            print(decodeline, end=end)
                            time.sleep(0.1)
            except (KeyboardInterrupt):
                print("[embARC] Terminate batch job")
                sys.exit(1)

    except OSError as e:
        if e.args[0] == errno.ENOENT:
            print(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by \
                executing \"%s\".\n" % (command[0], command[0]), e.args[0])
        else:
            raise e
    except Exception as e:
        print(e)
    proc.wait()
    if os.path.exists(file_name):
        os.remove(file_name)
    if proc.stdout:
        proc.stdout.close()
    if proc.stderr:
        proc.stderr.close()
    del proc
    return build_out


def pqueryTemporaryFile(command):
    current_command = None
    if isinstance(command, list):
        current_command = " ".join(command)
    else:
        current_command = command
    print("[embARC] Run command {}".format(current_command))
    proc = None
    returncode = 0
    rt_list = None
    file_num = random.randint(100000, 200000)
    file_name = "message" + str(file_num) + ".log"
    try:
        log_file = open(file_name, "w")
        proc = subprocess.Popen(current_command, stdout=log_file, stderr=None, shell=True)
        log_file.close()
        returncode = proc.wait()

    except Exception as e:
        print("[embARC] Run command {} failed : {}".format(current_command, e))
    if os.path.exists(file_name):
        with open(file_name) as f:
            rt_list = f.read().splitlines()
        os.remove(file_name)
    del proc
    return returncode, rt_list
