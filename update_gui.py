""" 更新主体程序,GUI组件页面呈现
:author: 闻煜
:time: 2022/09/30
"""
import os
import subprocess
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import util
from update_ui import Ui_MainWindow
from update import Update, log
from config import UPDATE_SIGNAL


def main() -> None:
    """ 主函数, 程序从该函数运行 """

    # 判断是否需要更新
    update = Update()
    update_versions = update.getUpdateVersions()
    if len(update_versions) == 0:
        log('没有新版本需要更新!')
        return

    # 主体ui程序运行
    try:
        app = QApplication(sys.argv)
        updater_widget = UpdaterWidget()
        updater_widget.setup_ui()
        updater_widget.worker()
        app.exec_()
    except BaseException as e:
        log(e)

    return


class UpdaterWidget(QWidget):
    """ 更新程序Widget组件 """

    def __init__(self):
        """ 构造函数初始化，初始化相关变量 """

        super(UpdaterWidget, self).__init__()
        self.main_widget = QMainWindow()  # 主窗体
        self.update_ui = Ui_MainWindow()  # designer设计的UI窗体组件
        self.updater = Updater()  # 更新线程

    def setup_ui(self):
        """ 安装加载ui并且设置一些初值 """

        self.update_ui.setupUi(self.main_widget)
        self.update_ui.plainTextEdit.setPlainText('正在更新...')
        self.update_ui.progressBar.setValue(0)

        # 配置信号与槽
        self.config_signal_and_slot()

    def worker(self) -> None:
        """ 开启工作线程 """

        self.updater.start()

        return

    def config_signal_and_slot(self) -> None:
        """ 配置信号与槽 """

        def handle_completed(flag):
            """ 更新成功后处理事件 """
            def handle_click():
                """ 点击更新完成后事件处理 """

                # 更新完成
                log('更新完成！')

                # 启动应用程序
                # 判断应用程序是否存在
                is_exist = os.path.exists(self.updater.update.config.application)
                if is_exist:
                    subprocess.Popen(self.updater.update.config.application, close_fds=True)
                else:
                    log('找不到用户程序 {}'.format(self.updater.update.config.application))
                    self.updater.update.config.writeConfigFile('update', 'exitCode', '1')
                    sys.exit(1)  # 找不到用户程序

                # 正常退出
                sys.exit(0)

            # 弹出更新完成对话框
            if flag:
                msg = QMessageBox()
                msg.setText('更新完成！')
                msg.setWindowTitle('更新')
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(handle_click)
                msg.exec_()

        # 配置信号与槽函数
        UPDATE_SIGNAL.currVersion.connect(lambda v: self.update_ui.current_version_label.setText('当前版本：' + v))
        UPDATE_SIGNAL.newVersion.connect(lambda v: self.update_ui.new_version_label.setText('最新版本：' + v))
        UPDATE_SIGNAL.completed.connect(handle_completed)
        UPDATE_SIGNAL.log.connect(lambda i: self.update_ui.plainTextEdit.appendPlainText(i))
        UPDATE_SIGNAL.progress.connect(lambda i: self.update_ui.progressBar.setValue(i))

        return


class Updater(QThread):
    """ 工作线程，负责启动更新 """

    def __init__(self) -> None:
        """ 构造函数初始化，初始化相关变量 """

        super(Updater, self).__init__()

        # 创建更新对象，初始化相关配置
        self.update = Update()

        return

    def run(self):
        """ 更新线程主体运行方法，负责执行更新操作 """

        log('启动参数: {}'.format(str.join(' ', sys.argv)))
        log('配置文件路径: {}'.format(self.update.config.configFilePath))

        # 获得当前版本
        UPDATE_SIGNAL.currVersion.emit(self.update.config.version)
        log('程序当前版本: ' + self.update.config.version)

        # 获得最新版本
        new_versions = self.update.getUpdateVersions()
        if len(new_versions) != 0:
            UPDATE_SIGNAL.newVersion.emit(new_versions[len(new_versions) - 1])
            log('程序最新版本: ' + new_versions[len(new_versions) - 1])

        # 终止应用程序异常处理
        log('父进程PID:' + str(os.getppid()))
        log('本进程PID:' + str(os.getpid()))
        pids = util.kill_process(self.update.config.application)  # 终止应用程序
        log('终止进程, PID: {}, NAME: {}.'.format(pids, self.update.config.application))

        # 启动更新
        self.update.run()

        # 更新结束
        UPDATE_SIGNAL.completed.emit(True)
        UPDATE_SIGNAL.log.emit('程序更新完成.')

        return


if __name__ == '__main__':
    main()
