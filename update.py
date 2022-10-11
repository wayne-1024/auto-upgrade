""" 更新主体程序
:author: 闻煜
:time: 2022/09/27
"""
import os.path
import re
import shutil
import sys
import time
import urllib.request
import bsdiff4
import urllib3.exceptions
from html.parser import HTMLParser
import urllib3
from config import UpdaterConfigInfo, UPDATE_SIGNAL
import util


def main():
    """ 主函数, 程序从该函数运行 """

    # 打印版本号，测试config配置信息
    update = Update()
    print('version: ', update.config.version)
    update.config.writeConfigFile('program', 'version', '2.0')
    update.config.refresh()
    print('version: ', update.config.version)

    # 测试loadUrl, 获得版本号列表
    vl = update.loadUrl()
    print("load version list: ", vl)

    # 测试getUpdateVersions, 获得更新列表
    uvl = update.getUpdateVersions()
    print("update version list: ", uvl)

    # 测试run
    update.run()

    return


def log(info: str) -> None:
    """ 日志处理 """

    UPDATE_SIGNAL.log.emit(info)
    print('[{}][info] '.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), info)

    update_config = UpdaterConfigInfo()
    log_path = os.path.dirname(update_config.logPath)
    if not os.path.exists(log_path):
        print('日志路径不存在，正在创建目录.')
        os.makedirs(log_path)

    with open(update_config.logPath, 'a') as f:
        f.write('[{}][info] {}\n'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), info))


def compare_version(version1: str, version2: str) -> int:
    """ 比较版本号version1和version2。
    版本号由一个或多个修订号组成，各修订号由一个 '.' 连接。
    每个修订号由多位数字组成，可能包含前导零 。每个版本号至少包含一个字符。
    修订号从左到右编号，下标从 0 开始，最左边的修订号下标为 0 ，下一个修订号下标为 1 ，以此类推。
    例如，2.5.33 和 0.1 都是有效的版本号。
    比较版本号时，请按从左到右的顺序依次比较它们的修订号。
    比较修订号时，只需比较 忽略任何前导零后的整数值 。
    也就是说，修订号 1 和修订号 001 相等 。
    如果版本号没有指定某个下标处的修订号，则该修订号视为 0 。
    例如，版本 1.0 小于版本 1.1 ，因为它们下标为 0 的修订号相同，而下标为 1 的修订号分别为 0 和 1 ，0 < 1 。

    :param version1: 版本号1
    :param version2: 版本号2
    :return: 如果version1>version2, 返回1, 如果version1<version2, 返回-1, 除此之外返回0
    """
    arr1 = version1.split('.')
    arr2 = version2.split('.')
    max_length = max(len(arr1), len(arr2))
    for i in range(0, max_length):
        num1 = int(arr1[i]) if i < len(arr1) else 0
        num2 = int(arr2[i]) if i < len(arr2) else 0
        if num1 == num2:
            continue
        return 1 if num1 > num2 else -1

    return 0


class Update:
    """ 更新程序类，主要负责更新 """

    def __init__(self, config_path: str = 'update.ini') -> None:
        """ 构造函数，初始化变量信息 """

        self.config = UpdaterConfigInfo(config_path)
        self.updateVersionList = []

        return

    def run(self) -> None:
        """ 执行更新过程 """

        # TODO LOG 日志处理优化
        log('正在加载文件服务器:{}.'.format(self.config.serverUrl))

        # 1）加载更新地址，获取更新列表
        update_version_list = self.getUpdateVersions()

        log('访问文件服务器成功，更新列表:{}.'.format(self.updateVersionList))

        # 2）判断是否需要更新
        if len(update_version_list) == 0:
            print('无新版本！')
            return

        # 3）根据更新列表逐一操作
        for i in range(0, len(update_version_list)):
            # 3.1）拉取更新包
            log('正在拉取更新包:{}.'.format(update_version_list[i]))
            self.__fetch(update_version_list[i])
            # 3.2）解压并合并更新包
            log('正在合并{}更新包.'.format(update_version_list[i]))
            self.__patch(update_version_list[i])
            log('版本{}更新成功.'.format(update_version_list[i]))

        # 更新成功
        self.config.writeConfigFile('update', 'exitCode', '0')
        return

    def loadUrl(self) -> list:
        """ 从文件服务器加载数据, 从中爬取软件名称，提取版本号

        :return: 版本号列表
        """

        class UpdateHTMLParser(HTMLParser):
            """ HTMLParser类，用于解析HTML树 """

            def __init__(self, update: Update = self):
                """ 构造函数， 初始化相关信息 """
                super(UpdateHTMLParser, self).__init__()
                self.update = update

            def handle_data(self, data: str) -> None:
                """ 处理标签内数据，例如<a>data</a>，提取data。
                将data解析为版本名字,然后提取版本号到update_version_list保存。

                :param data: 标签数据
                :return:
                """
                version_name = re.match(self.update.config.programName +
                                        r'\d+(.\d+)*', data)  # 匹配版本号(含软件名字) eg: app_name1.0

                if version_name is not None:
                    curr_version = version_name.group()
                    # 提取版本号 eg: "app_name1.0" -> "1.0"
                    self.update.updateVersionList.append(curr_version[len(self.update.config.programName):])

        # 加载软件目录,借助正则表达式提取版本号, 返回版本号数组
        try:
            http = urllib3.PoolManager()
            request = http.request('GET', self.config.serverUrl)  # 通过url访问下载目录
        except urllib3.exceptions.HTTPError as e:
            print('load url {} error, reason: {} !'.format(self.config.serverUrl, e.reason))
            self.config.writeConfigFile('update', 'exitCode', '2')
            sys.exit(2)  # http错误，网络错误

        self.updateVersionList = []  # 清空版本号列表

        parser = UpdateHTMLParser(update=self)
        parser.feed(request.data.decode('utf-8'))  # 解析版本号

        # 将版本号从大到小排序
        self.updateVersionList.sort(key=util.cmp_to_key(compare_version))

        return self.updateVersionList

    def getUpdateVersions(self) -> list:
        """ 获取更新列表

        :return: 返回更新列表
        """

        # 加载版本列表, 并刷新读取配置信息
        self.loadUrl()
        self.config.refresh()

        # 迭代判断版本号列表，将大版本加入更新列表中
        update_version_list = []  # 更新列表
        for i in range(0, len(self.updateVersionList)):
            # 如果比当前版本号大，版本号列表添加版本
            if compare_version(self.updateVersionList[i], self.config.version) == 1:
                update_version_list.append(self.updateVersionList[i])

        # 将更新列表状态更新
        self.updateVersionList = update_version_list

        return update_version_list

    def __fetch(self, update_version: str) -> None:
        """ 根据文件名称到指定下载地址下载更新补丁

        :param update_version: 更新版本号
        """

        def schedule(block_num: int, bs: int, size: int) -> int:
            """ hook函数，用于统计并显示下载进度。

            :param block_num: 已经下载的数据块
            :param bs: 数据块大小
            :param size: 远程文件大小
            :return: 当前下载进度
            """

            # 下载进度计算
            percent = 100 * block_num * bs / size
            if percent > 100:
                percent = 100

            # TODO LOG 处理进度
            UPDATE_SIGNAL.progress.emit(percent)

            return percent

        # 刷新配置文件
        self.config.refresh()

        # 设置下载信息
        fn = self.config.programName + update_version  # 含有版本号的文件名称
        download_url = self.config.serverUrl + fn + '/' + fn + '.zip'  # 文件下载地址

        # 下载文件，下载过程中使用hook处理函数schedule处理结果
        try:
            urllib.request.urlretrieve(download_url, filename=fn+'.zip', reporthook=schedule)
        except urllib.error.HTTPError as e:
            # TODO 日志处理
            print('fetch {} version error, reason: {}, code: {}!'
                  .format(update_version, e.reason, e.code))
            self.config.writeConfigFile('update', 'exitCode', '3')
            sys.exit(3)  # 发布包错误，访问不到 || 网络错误

        return

    def __patch(self, update_version: str) -> None:
        """ 解压并合并文件

        :param update_version: 更新的版本号
        """

        # 判断补丁更新目录是否存在，如果不存在，就创建
        if not os.path.exists(self.config.patchPath):
            os.makedirs(self.config.patchPath)

        # 1）解压更新包
        util.unzip(self.config.programName + update_version + '.zip', self.config.patchPath)

        # 2）解析version文件
        version_info = util.read_json(os.path.join(self.config.patchPath, 'version'))
        log('{}版本文件信息: {}'.format(update_version, version_info))

        # 3）判断是否需要启用增量更新，然后执行更新操作， 增量更新需要先清空程序文件夹
        if not version_info['incUpdateFlag']:  # 启用全量更新
            self.__remove_files()  # 清除应用程序文件夹

        # 增量更新，合并新版本
        self.__merge()

        # 4）更新配置文件，设置新版本号
        self.config.writeConfigFile('program', 'version', update_version)

        # 5）删除tmp文件夹及压缩包
        shutil.rmtree(self.config.patchPath)
        if os.path.exists(self.config.programName + update_version + '.zip'):
            os.remove(self.config.programName + update_version + '.zip')

        return

    def __merge(self) -> None:
        """ 合并文件 """

        version_info = util.read_json(os.path.join(self.config.patchPath, 'version'))

        # 迭代版本文件
        # 其中files和file为关键字，由version版本文件约束，此处为硬编码
        for file in version_info['files']:
            # 1）TODO 校验MD5

            # 2）合并（新增）文件
            if file['patch']:  # 打补丁
                bsdiff4.file_patch(os.path.join(self.config.programPath, file['path']),
                                   os.path.join(self.config.programPath, file['path']),
                                   os.path.join(self.config.patchPath, file['patchFile']))
            else:  # 新增(拷贝)文件
                if not os.path.isdir(os.path.join(self.config.patchPath, file['path'])):
                    shutil.copyfile(os.path.join(self.config.patchPath, file['path']),
                                    os.path.join(self.config.programPath, file['path']))
                else:
                    shutil.copytree(os.path.join(self.config.patchPath, file['path']),
                                    os.path.join(self.config.programPath, file['path']))

        return

    def __remove_files(self) -> None:
        """ 删除应用程序除忽略以外的文件或目录 """

        ignores = self.config.ignoreFiles

        for root, dirs, files in os.walk(self.config.programPath):
            ignores = ignores + [os.path.join(root, item) for item in ignores]
            dir_list = [os.path.join(root, item) for item in dirs]

            for dir_item in dir_list:
                if dir_item in ignores:
                    dirs.remove(dir_item.split(self.config.split)[-1])  # 根据分隔符分割
                    continue
                dirs.remove(dir_item.split(self.config.split)[-1])
                shutil.rmtree(dir_item)

            for file in files:
                if file in self.config.ignoreFiles:
                    continue
                os.remove(os.path.join(self.config.programPath, file))


if __name__ == '__main__':
    main()
