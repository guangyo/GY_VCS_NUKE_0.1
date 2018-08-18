#coding:utf8
import sys,os,re,subprocess
import use_path
from PySide import QtCore,QtGui
import Merge_track,Xml_info,Edl_info,Time_conversion,ImageHash
from main_windows_ui import Ui_Form 
from main_windows import *
if __name__=="__main__":
    app=QApplication(sys.argv)
    main_app=Main_win()
    if  main_app.connect_to_cgteamwork():
        main_app.add_cgteamwork_to_combobox()
        main_app.show()
        sys.exit(app.exec_())
