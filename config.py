""" 配置文件
:author: 闻煜
:time: 2022/09/10
"""
import configparser
import platform
from PyQt5.QtCore import QObject, pyqtSignal


def main() -> None:
    """ 主函数, 程序从该函数运行 """

    # 测试更新程序配置信息
    update_config_info = UpdaterConfigInfo()
    print(update_config_info.version)
    update_config_info.writeConfigFile('program', 'version', '1.0')
    update_config_info.refresh()  # 建议写入之后重新刷新读取
    print(update_config_info.version)

    return


class UpdaterConfigInfo:
    """ 更新程序配置信息 """

    def __init__(self, config_file_path: str = 'update.ini') -> None:
        """ 构造函数，初始化基本信息
        配置文件ini格式为, eg:
        ------------------------------------------------------>
        [program]
        ; 应用程序名称
        name = app
        application = app.exe
        version = 1.1                      ; 应用程序当前版本号
        path = .                           ; 应用程序目录
        patch_path = .\tmp                 ; 补丁(更新)目录
        ignore_files = update.exe:version  ; 忽略更新文件, 以:分割

        [server]
        ; 文件服务器地址, 末尾/不可省略
        url = http://localhost:1024/demoapp2/
        <-----------------------------------------------------
        默认忽略文件目录：'version', 'update_gui.exe', 'update.exe', 'update.ini',
        'tmp', 'update.log', 'update', 'update_gui'.

        :param config_file_path: 配置文件路径，默认为./update.ini
        """

        # 配置文件路径
        self.configFilePath = config_file_path

        # 使用configparser处理ini文件
        config = configparser.ConfigParser()
        config.read(config_file_path)

        # 读取配置文件，对变量初始化
        self.programName = config.get('program', 'name')
        self.application = config.get('program', 'application')
        self.version = config.get('program', 'version')
        self.programPath = config.get('program', 'path')
        self.patchPath = config.get('program', 'patch_path')
        self.ignoreFiles = config.get('program', 'ignore_files').split(':')
        self.logPath = config.get('program', 'log_path')
        self.serverUrl = config.get('server', 'url')
        self.exitCode = config.get('update', 'exitCode')

        # 默认忽略配置文件和目录
        self.ignoreFilesDefault = ['version', 'update_gui.exe', 'update.exe', 'log',
                                   'update.ini', 'tmp', 'update.log', 'update', 'update_gui']
        self.ignoreFiles = self.ignoreFiles + self.ignoreFilesDefault

        # 路径分隔符
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

    def writeConfigFile(self, section: str, key: str, val: str) -> bool:
        """ 将信息写回配置文件

        :param section: ini文件节
        :param key: ini文件key
        :param val: ini文件value
        """

        # 使用configparser处理ini文件
        config = configparser.ConfigParser()
        config.read(self.configFilePath)

        # 根据key-value设置
        config[section][key] = val

        # 将配置写入ini文件
        try:
            file = open(self.configFilePath, 'w')
            config.write(file)
        except OSError as reason:
            # TODO 日志处理
            print('error:' + reason)
            return False
        finally:
            file.close()

        # 刷新读取配置信息
        self.refresh()

        return True

    def refresh(self) -> None:
        """ 重新读取配置信息，更新状态 """

        # 配置文件路径
        self.configFilePath = self.configFilePath

        # 使用configparser处理ini文件
        config = configparser.ConfigParser()
        config.read(self.configFilePath)

        # 读取配置文件，对变量初始化
        self.programName = config.get('program', 'name')
        self.application = config.get('program', 'application')
        self.version = config.get('program', 'version')
        self.programPath = config.get('program', 'path')
        self.patchPath = config.get('program', 'patch_path')
        self.ignoreFiles = config.get('program', 'ignore_files').split(':')
        self.ignoreFiles = self.ignoreFiles + self.ignoreFilesDefault
        self.logPath = config.get('program', 'log_path')
        self.serverUrl = config.get('server', 'url')
        self.exitCode = config.get('update', 'exitCode')

        return


class UpdateSignal(QObject):
    """ 设置信号 """
    currVersion = pyqtSignal(str)  # 当前版本信号
    newVersion = pyqtSignal(str)   # 最新版本信号
    completed = pyqtSignal(int)    # 更新完成信号
    log = pyqtSignal(str)          # 日志信息信号
    progress = pyqtSignal(int)     # 更新进度信号


UPDATE_SIGNAL = UpdateSignal()


if __name__ == '__main__':
    main()
