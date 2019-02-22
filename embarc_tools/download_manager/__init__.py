from __future__ import print_function, unicode_literals

import os
import stat
import urllib
import contextlib
from os import listdir, remove, makedirs
import sys
from shutil import copyfile
import shutil
import zipfile
import tarfile
import yaml
import json
cwd_root = ""
_cwd = os.getcwd()


def getcwd():
    '''return current working path '''
    global _cwd
    return _cwd


@contextlib.contextmanager
def cd(newdir):
    '''A function that does cd'''
    global _cwd
    prevdir = getcwd()
    os.chdir(newdir)
    _cwd = newdir
    try:
        yield
    finally:
        os.chdir(prevdir)
        _cwd = prevdir


def relpath(root, path):
    '''return the relative path of root and path'''
    return path[len(root) + 1:]


def mkdir(path):
    '''A function that does mkdir'''
    if not os.path.exists(path):
        makedirs(path)


def rmtree_readonly(directory):
    '''change permission and delete directory'''
    if os.path.islink(directory):
        os.remove(directory)
    else:
        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(directory, onerror=remove_readonly)


def delete_dir_files(directory, dir=False):
    """ A function that does rm -rf

    Positional arguments:
    directory - the directory to remove
    """
    if not os.path.exists(directory):
        return
    if os.path.isfile(directory):
        remove(directory)
    else:
        if not dir:
            for element in listdir(directory):
                to_remove = os.path.join(directory, element)
                if not os.path.isdir(to_remove):
                    remove(to_remove)
        else:
            shutil.rmtree(directory)


def generate_file(filename, data, path=None):
    file = None
    if path and os.path.exists(path) and os.path.isdir(path):
        file = os.path.join(path, filename)
    else:
        file = os.path.join(os.getcwd(), filename)
    if os.path.isfile(file):
        os.remove(file)
    try:
        with open(file, 'w+') as f:
            f.write(data)
        f.close()
    except EnvironmentError:
        print("[embARC] Unable to open %s for writing!" % file)
        return -1
    print("[embARC] Write to file %s" % file)
    return 0


def generate_yaml(filename, data):
    file = os.path.join(os.getcwd(), filename)
    if os.path.isfile(file):
        os.remove(file)
    try:
        with open(file, 'w+') as f:
            f.write(yaml.dump(data, default_flow_style=False))
        f.close()
    except EnvironmentError:
        print("[embARC] Unable to open %s for writing!" % file)
        return -1
    print("[embARC] Write to file %s" % file)
    return 0


def edit_yaml(filename, data):
    file = os.path.join(os.getcwd(), filename)
    if not os.path.isfile(file):
        generate_yaml(filename, data)
        return
    else:
        try:
            with open(file, 'w+') as f:
                f.write(yaml.dump(data, default_flow_style=False))
        except EnvironmentError:
            print("[embARC] Unable to open %s for writing!" % file)
            return -1
        print("[embARC] Write to file %s" % file)
        return 0


def read_json(path):
    result = None
    with open(path, "r") as f:
        result = json.load(f)
    return result


def generate_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
        f.close()


def copy_file(src, dst):
    """ Implement the behavior of "shutil.copy(src, dst)" without copying the
    permissions (this was causing errors with directories mounted with samba)

    Positional arguments:
    src - the source of the copy operation
    dst - the destination of the copy operation
    """
    if os.path.isdir(dst):
        _, base = os.path.split(src)
        dst = os.path.join(dst, base)
    copyfile(src, dst)


def download_file(url, path):
    '''from url download file to path. if failed ,return False. else return True'''
    try:
        urllib.urlretrieve(url, path)
    except AttributeError:
        from urllib import request
        request.urlretrieve(url, path)
    except Exception as e:
        print("[embARC] This file from %s can't be download for %s" % (url, e))
        sys.stdout.flush()
        return False
    return True


def unzip(file, path):
    '''extract file from .zip to path
    file - the path of zip
    path - the dest path
    return directory name after decompression'''
    file_name = None
    try:
        pack = zipfile.ZipFile(file, "r")
        files = pack.namelist()
        file_name = files[0]
        pack.extractall(path)
        pack.close()

    except Exception as e:
        print(e)
    return file_name


def untar(file, path):
    file_name = None
    try:
        pack = tarfile.open(file, "r:gz")
        files = pack.getnames()
        file_name = files[0]
        for file in files:
            pack.extract(file, path)
        pack.close()
    except Exception as e:
        print(e)
    return file_name


def extract_file(file, path):
    extract_file_name = None
    extract_file_path = None
    _, filesuffix = os.path.splitext(file)
    if filesuffix == ".gz":
        extract_file_name = untar(file, path)
    elif filesuffix == ".zip":
        extract_file_name = unzip(file, path)
    else:
        print("[embARC] This file {} can't be extracted".format(file))
    if extract_file_name is not None:
        extract_file_path = os.path.join(path, extract_file_name)
    return extract_file_path


def show_progress(title, percent, max_width=80):
    '''show progress when download file'''
    if sys.stdout.isatty():
        percent = round(float(percent), 2)
        show_percent = '%.2f' % percent
        bwidth = max_width - len(str(title)) - len(show_percent) - 6  # 6 equals the spaces and paddings between title, progress bar and percentage
        sys.stdout.write('%s |%s%s| %s%%\r' % (str(title), '#' * int(percent * bwidth // 100), '-' * (bwidth - int(percent * bwidth // 100)), show_percent))
        sys.stdout.flush()


def hide_progress(max_width=80):
    if sys.stdout.isatty():
        sys.stdout.write("\r%s\r" % (' ' * max_width))
