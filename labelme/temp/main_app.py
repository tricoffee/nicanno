# -*- coding: utf-8 -*-


import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from QThread_Example_UI import Ui_Form
from tutils import list_files,SupportImageType

#class MyMainForm(QMainWindow, Ui_Form, QThread):
class MyMainForm(QMainWindow, Ui_Form):
    trigger = pyqtSignal([list,int])

    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        #self.runButton.clicked.connect(self.execute)
        imgdir = r"C:\BaiduNetdisk\Day20210624"
        self.fnms = list_files(imgdir,SupportImageType)
        self.execute()

    def execute(self):
        self.trigger.connect(self.display)
        self.trigger.emit(self.fnms,len(self.fnms))
        

        

    def display(self,xlist,x):
        # 由于自定义信号时自动传递一个字符串参数，所以在这个槽函数中要接受一个参数
        self.listWidget.clear()
        for i in range(x):
            self.listWidget.addItem(xlist[i])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.show()
    sys.exit(app.exec_())