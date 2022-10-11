""" 安装打包工具，用于打包应用程序
:author: 闻煜
:time: 2022/09/23
"""
import os
import platform


def main() -> None:
    """ 主函数, 程序从该函数开始运行。

    :return:
    """
    install()

    return None


def install() -> bool:
    """ 将工具自动打包

    :return:
    """
    # 打包vbuilder.py为exe
    if platform.system() == "Windows":
        os.system("pyinstaller.exe -F -i .\\icon\\version.ico .\\vbuilder.py")
    else:
        os.system("pyinstaller -F -i ./icon/version.ico ./vbuilder.py")

    # 打包update_gui.py为exe
    if platform.system() == "Windows":
        os.system("pyinstaller.exe -F -i .\\icon\\update.ico .\\update_gui.py")
    else:
        os.system("pyinstaller -F -i ./icon/update.ico ./update_gui.py")

    return True


if __name__ == '__main__':
    main()
