from numba.cuda import selp

​

from kiwoom.kiwoom import *

from PyQt5.QtWidgets import *\

​

import sys

​

​

class Ui_class():

def __init__(self):

#print("UI 클래스")

​

self.app = QApplication(sys.argv)

​

self.kiwoom = Kiwoom()

# 프로그램 종료되지 않도록.

self.app.exec_()
