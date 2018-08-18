# -*- coding: utf-8 -*-
import os
import sys

from lib_path import *

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
QApplication.addLibraryPath(G_lib_pyside_path+"/PySide2/plugins/")
from create_shot import *

if __name__ == "__main__":
    app = QApplication(sys.argv)
    create = create_shot_widget()
    create.init_check_info()
    create.show() 
        
    sys.exit(app.exec_())

