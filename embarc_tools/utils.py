from __future__ import print_function, unicode_literals
from functools import reduce
import sys
import operator
import os
from os import listdir, remove, makedirs
import urllib
import contextlib
import shutil
import zipfile
import tarfile
import json
import pkgutil
import importlib

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


def read_json(path):
    result = None
    with open(path, "r") as f:
        result = json.load(f)
    return result


def generate_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
        f.close()


def download_file(url, path):
    '''from url download file to path. if failed ,return False. else return True'''
    try:
        urllib.urlretrieve(url, path)
    except AttributeError:
        from urllib import request
        request.urlretrieve(url, path)
    except Exception as e:
        print(f"[embARC] This file from {url} can't be download for {e}")
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
        print(f"[embARC] This file {file} can't be extracted")
    if extract_file_name is not None:
        extract_file_path = os.path.join(path, extract_file_name)
    return extract_file_path


def merge_recursive(*args):
    if all(isinstance(x, dict) for x in args):
        output = {}
        keys = reduce(operator.or_, [set(x) for x in args])

        for key in keys:
            # merge all of the ones that have them
            output[key] = merge_recursive(*[x[key] for x in args if key in x])

        return output
    return reduce(operator.add, args)


def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    results = {}
    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        if not is_pkg:
            results[name] = importlib.import_module(full_name)
        elif recursive:
            results.update(import_submodules(full_name))
    return results
