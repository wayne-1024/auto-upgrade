""" 工具类，提供一些常用工具函数
:author: 闻煜
:time: 2022/09/13
"""
import hashlib
import json
import os
import shutil
from typing import Callable
import zipfile

import psutil


def get_file_size(fp: str) -> int:
    """ 获取文件大小，以字节byte为单位

    :param fp: 文件路径
    :return:
    """
    file_size = os.path.getsize(fp)
    return file_size


def get_file_md5(file: str) -> str:
    """ 获取文件MD5值。

    :param file: 文件路径
    :return: 文件MD5值
    """
    with open(file, 'rb') as fp:
        data = fp.read()
    md5 = hashlib.md5(data).hexdigest()  # TODO 大文件md5
    return md5


def check_md5(file: str, file_md5: str) -> str:
    """ 校验文件file的MD5值与给定file_md5是否一致。

    :param file: 校验文件路径
    :param file_md5: 校验文件给定MD5值
    :return: 校验结果，一致返回True，不一致返回False
    """
    md5 = get_file_md5(file)
    if file_md5 == md5:
        return True
    else:
        return False


def save_json(json_dict: {}, file: str) -> None:
    """ 将json_info数据保存到文件file。

    :param json_dict: json数据字典
    :param file: 保存文件
    :return:
    """
    json_info = json.dumps(json_dict, indent=4, separators=(',', ':'))
    with open(file, 'w', encoding='utf-8') as f:
        f.write(json_info)


def read_json(path: str) -> {}:
    """ 根据path文件路径读取json数据。

    :param path: json文件路径
    :return: json数据，以字典形式返回
    """
    with open(path, 'r') as file:
        json_dict = json.load(file)
    return json_dict


def recurse_dir(path: str, func: Callable[..., None], ignore_dirs: list = []) -> None:
    """ 递归遍历目录path，对目录中的每个文件执行func函数。

    :param path: 目录路径
    :param func: 回调函数
    :param ignore_dirs: 忽略目录
    :return:
    """
    for root, dirs, files in os.walk(path):
        if root in ignore_dirs:
            continue
        for file in files:
            func(file)


def unzip(file: str, extract_dir: str) -> bool:
    """ 解压文件file(含路径)全部至目录extract_dir

    :param file: 压缩文件(zip格式), 含路径
    :param extract_dir: 解压目录
    :return: 解压是否成功
    """
    z_file = zipfile.ZipFile(file, 'r')
    z_file.extractall(extract_dir)
    z_file.close()
    return True


def compress(dir_path: str, compress_dir: str = '') -> bool:
    """ 将目录压缩至路径compress_dir。

    :param dir_path: 目录路径
    :param compress_dir: 压缩包放置路径, 默认为压缩目录上一级
    :return:
    """
    compress_file_name = dir_path + '.zip'  # 压缩文件名字

    # 压缩文件
    z = zipfile.ZipFile(compress_file_name, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dir_path):
        f_path = root.replace(dir_path, '')
        f_path = f_path and f_path + os.sep or ''
        for file in files:
            z.write(os.path.join(root, file), f_path+file)
    z.close()

    # 将压缩包移动至指定路径
    if compress_dir != '':
        shutil.move(compress_file_name, compress_dir)  # 将压缩文件移动至压缩目录compress_dir路径

    return True


def kill_process(process_name: str) -> list:
    """ 根据进程名process_name关闭进程

    :process_name: 进程名
    :return: 关闭的进程PID列表
    """

    pids = psutil.process_iter()  # 所有进程信息
    pid_list = []

    for pid in pids:
        if pid.name() == process_name:
            os.system('taskkill /PID {} /F'.format(pid.pid))  # 关闭进程
            print('终止进程, PID: {}, NAME: {}.'.format(pid.pid, process_name))
            pid_list.append(pid.pid)

    return pid_list


def cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function"""

    class K(object):
        __slots__ = ['obj']

        def __init__(self, obj):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        __hash__ = None

    return K
