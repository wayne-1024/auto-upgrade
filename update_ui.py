# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\update-gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(346, 220)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.current_version_label = QtWidgets.QLabel(self.centralwidget)
        self.current_version_label.setGeometry(QtCore.QRect(20, 20, 111, 16))
        self.current_version_label.setObjectName("current_version_label")
        self.new_version_label = QtWidgets.QLabel(self.centralwidget)
        self.new_version_label.setGeometry(QtCore.QRect(230, 20, 111, 16))
        self.new_version_label.setObjectName("new_version_label")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(20, 170, 321, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 50, 291, 101))
        self.groupBox.setObjectName("groupBox")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.groupBox)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 20, 271, 71))
        self.plainTextEdit.setStyleSheet("border: none;\n"
"background: rgba(0,0,0,0);\n"
"")
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName("plainTextEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # 禁止最大化按钮
        # MainWindow.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

        MainWindow.show()


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "更新"))
        self.current_version_label.setText(_translate("MainWindow", "当前版本：1.0"))
        self.new_version_label.setText(_translate("MainWindow", "最新版本：*"))
        self.groupBox.setTitle(_translate("MainWindow", "状态"))
        self.plainTextEdit.setPlainText(_translate("MainWindow", "123123123"))

