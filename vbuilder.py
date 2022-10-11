""" 版本补丁更新工具,用于比对构建补丁文件和版本描述文件
:author: 闻煜
:time: 2022/09/27
"""
import argparse
import os.path
import platform
import time
from filecmp import dircmp
import bsdiff4
import util
import shutil


def main() -> None:
    """ 主函数, 程序从该函数运行 """

    # lp = '/Users/wayne/code/python/update-installer/updater/app'
    # rp = '/Users/wayne/code/python/update-installer/updater/app2.0'
    # builder = VersionBuilder(lp, rp)
    #
    # builder.version = 1.1
    #
    # # 测试build函数
    # builder.build()
    #
    # # 测试write函数，查看是否写入成功
    # builder.write()

    args_parser()

    return


def args_parser() -> None:
    """ 编写命令行工具 """

    # 设置命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('LeftPath', type=str, help=u'比对左侧目录，一般指旧版本程序目录', nargs='?')
    parser.add_argument('RightPath', type=str, help=u'比对右侧目录，一般指新版本程序目录', nargs='?')
    parser.add_argument('PatchPath', type=str, help=u'更新补丁生成目录,默认为./tmp', nargs='?', default='./tmp')
    parser.add_argument('-i', '--IgnoreFiles', type=str, help=u'比对需要忽略的文件或目录', nargs='?')
    parser.add_argument('-d', '--Description', type=str, help=u'版本描述', nargs='?')
    parser.add_argument('-v', '--VersionNumber', type=str, help=u'更新版本号', nargs='?')
    parser.add_argument('-V', '--Version', type=str, help=u'vbuilder版本', nargs='?')
    flag_parser = parser.add_mutually_exclusive_group(required=False)
    flag_parser.add_argument('-f', '--IncUpdateFlag', help=u'开启增量更新', dest='Flag', action='store_true')
    flag_parser.add_argument('-nf', '--No--IncUpdateFlag', help=u'关闭增量更新', dest='Flag', action='store_false')
    parser.set_defaults(flag=True)

    args = parser.parse_args()

    # 程序版本
    if args.Version:
        print('version:', '1.0')
        return

    # 判断命令行必要参数
    if not args.LeftPath:
        print('usage: vbuilder LeftPath RightPath PatchPath')
        return
    if not args.RightPath:
        print('usage: vbuilder LeftPath RightPath PatchPath')
        return
    if not args.PatchPath:
        print('usage: vbuilder LeftPath RightPath PatchPath')
        return
    if not args.IgnoreFiles:
        args.IgnoreFiles = []
    else:
        args.IgnoreFiles = args.IgnoreFiles.split(':')

    # 根据参数设置vbuilder
    builder = VersionBuilder(args.LeftPath, args.RightPath,
                             patch_path=args.PatchPath,
                             inc_update_flag=args.Flag,
                             ignore=args.IgnoreFiles)

    # 根据可选参数配置信息
    if args.Description:
        builder.description = args.Description
    if args.VersionNumber:
        builder.version = args.VersionNumber

    # 比对目录并构造
    builder.build()
    builder.write()


class VersionBuilder:
    """ 构造版本描述文件类
    版本描述文件，默认文件名称为version，
    默认采用json文件格式，格式描述如下：
    ---------------------------------------->
    {
      "version": "1.0",
      "description": "文件描述",
      "packageTime": "2022-09-20",
      "incUpdateFlag": true,
      "files": [
        {
          "patch": true,
          "path": "./app.exe",
          "patchFile": "./app.exe.patch",
          "md5": "ddd34fsdf2jiojfsdjfsdfj"
        },
        {
          "patch": false,
          "path": "./update.txt",
          "md5": "ddd3fsssf2jiojfsdjfs1fj"
        }
      ]
    }
    <----------------------------------------
    """

    def __init__(self, left_path: str, right_path: str, patch_path: str = './tmp',
                 ignore: list = None, inc_update_flag: bool = True) -> None:
        """ 构造函数，初始化成员变量 """

        # 读取配置信息
        self.leftPath = left_path
        self.rightPath = right_path
        self.patchPath = patch_path
        self.ignore = ignore

        # 设置版本描述文件名称，默认为version
        self.versionName = 'version'  # 版本描述文件名称

        # 版本描述文件基本信息
        self.version = ''                        # 更新版本号
        self.description = ''                    # 版本描述
        self.packageTime = ''                    # 打包时间
        self.incUpdateFlag = inc_update_flag     # 是否启用增量更新，默认启用
        self.files = []                          # 文件集合

        # 路径分隔符，根据不同系统平台适配不同分隔符
        self.split = '/'
        system_name = platform.system().lower()
        if system_name == 'windows':
            self.split = '\\'
        elif system_name == 'linux':
            self.split = '/'
        elif system_name == 'darwin':
            self.split = '/'
        else:
            self.split = '/'

        return

    def build(self) -> None:
        """ 根据文件路径生成版本描述文件 """

        def __buildDiff(left: str, right: str, cmp: dircmp, lp: str, rp: str) -> None:
            """ 根据新旧目录构建版本描述文件

            :param left: 左侧文件路径，一般使用老程序目录
            :param right: 右侧文件路径，一般使用新程序目录
            :param cmp: 比较对象
            :param lp: 左侧临时对象
            :param rp: 右侧临时对象
            """

            # 处理（新老版本）共同拥有的差异文件
            for item in cmp.diff_files:
                print('differ: ', lp + self.split + item)
                # print(util.get_file_md5(left + self.split + item))

                # 根据新老版本计算补丁文件，放置在文件目录，判断目录是否存在，如果不存在就创建目录
                fp1 = left + self.split + item
                fp2 = right + self.split + item
                rel_fp = os.path.join(self.patchPath, rp + self.split + item + '.patch')  # 目标文件相对路径

                # 设置文件版本描述信息
                file = {'patch': True, 'path': rp + self.split + item}

                if not os.path.exists(os.path.dirname(rel_fp)):
                    os.makedirs(os.path.dirname(rel_fp))
                bsdiff4.file_diff(fp1, fp2, rel_fp)

                file['patchFile'] = rp + self.split + item + '.patch'
                file['md5'] = util.get_file_md5(rel_fp)
                self.files.append(file)

            # 处理右侧（新版本）目录独有文件或目录
            for item in cmp.right_only:
                print('only in right: ', rp + self.split + item)

                # 将fp拷贝至rel_fp, eg: /user/code/app2.0/demo/app.exe -> ./demo/app.exe
                fp = right + self.split + item   # 源文件路径
                rel_fp = os.path.join(self.patchPath, rp + self.split + item)  # 目标文件相对路径

                # 设置文件版本描述信息
                file = {'patch': False, 'path': rp + self.split + item}

                if os.path.isfile(fp):  # 如果是文件
                    # print(util.get_file_md5(fp))  # 保存md5值
                    # 提取文件至当前目录，判断是否存在，如果不存在就使用makedirs递归创建目录
                    if not os.path.exists(os.path.dirname(rel_fp)):
                        os.makedirs(os.path.dirname(rel_fp))
                    file['md5'] = util.get_file_md5(fp)
                    shutil.copyfile(fp, rel_fp)
                else:  # 如果是目录
                    # 拷贝目录至补丁目录
                    shutil.copytree(fp, rel_fp)

                self.files.append(file)

            # 递归处理子目录，逐一比较
            for key in cmp.subdirs:
                __buildDiff(left + self.split + key, right + self.split + key, cmp.subdirs[key],
                            lp + self.split + key, rp + self.split + key)

            return

        # 输出基本比对路径
        print('left base path: ', self.leftPath)
        print('right base path: ', self.rightPath)

        # 目录比对, 结果保存至变量列表
        compare = dircmp(self.leftPath, self.rightPath, ignore=self.ignore)
        __buildDiff(self.leftPath, self.rightPath, compare, '.', '.')

        return

    def write(self) -> None:
        """ 将版本描述信息写入json文件 """

        # 设置基本信息
        self.packageTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 设置版本描述信息字典
        version_package = {
            'version': self.version,
            'description': self.description,
            'packageTime': self.packageTime,
            'incUpdateFlag': self.incUpdateFlag,
            'files': self.files
        }

        # 写入文件
        if not os.path.exists(self.patchPath):
            os.makedirs(self.patchPath)
        util.save_json(version_package, os.path.join(self.patchPath, self.versionName))

        return


if __name__ == '__main__' :
    main()
