# -*- coding: utf-8 -*-
#Author:王晨飞
#Time  :2017-12-29
#Describe:CgTeamWork V5整合
#         启动方式:   "C:/Program Files/Nuke10.5v4/Nuke10.5.exe --hiero --script D:/CgTeamWork/cgteamwork_v5/bin/base/hiero_plugin/hiero_start.py"


import os
import sys
import nuke
import shutil



G_base_path = os.path.dirname( os.path.dirname(__file__.replace("\\","/")) )
if not G_base_path in sys.path:
    sys.path.append( G_base_path )


G_cgtw_path = os.path.dirname( G_base_path ) + "/cgtw"
if not G_cgtw_path in sys.path:
    sys.path.append( G_cgtw_path )

import ct #德明 20180627 加载位置不对


G_plug_path = os.path.dirname( __file__.replace("\\","/") )
if not G_plug_path in sys.path:
    sys.path.append( G_plug_path )


from hiero_plugin  import *

from PySide.QtGui  import *
from PySide.QtCore import *

from hiero.core    import *
from hiero.ui      import *



def start_before():

    t_workspace_sou_path = unicode(os.path.join(os.path.dirname(__file__),"cgtw.xml")).replace("\\","/")
    t_workspace_des_path = False
    t_QtWebKit4_sou_path = False
    t_QtWebKit4_des_path = False
    for evn_path in nuke.nuke.pluginPath():
        if os.path.basename( evn_path ) == ".nuke":
            t_workspace_des_path = evn_path + "/Workspaces/Hiero/cgtw.xml"
        if os.path.basename( evn_path ) == "plugins":
            t_QtWebKit4_sou_path = os.path.dirname( evn_path ) + "/QtWebKit4.dll"
            t_QtWebKit4_des_path = os.path.dirname( evn_path ) + "/pythonextensions/site-packages/PySide/QtWebKit4.dll"            
    if t_workspace_des_path==False or t_QtWebKit4_sou_path==False or t_QtWebKit4_des_path==False:
        return False
    

    if not os.path.exists( os.path.dirname(t_workspace_des_path) ):
        try:
            os.makedirs( os.path.dirname(t_workspace_des_path) )
        except Exception,e:
            print e
            
            
            
            
    if not os.path.exists( t_workspace_des_path ):
        try:
            #===============骁颖==2018.06.15=====================
            #shutil.copy2(t_workspace_sou_path, t_workspace_des_path)
            ct.file().copy_file(t_workspace_sou_path, t_workspace_des_path)
            #===============骁颖==2018.06.15=====================
        except Exception,e:
            print e
            
            
            
    if os.path.exists( t_QtWebKit4_sou_path ) and not os.path.exists( t_QtWebKit4_des_path ):
        try:
            #===============骁颖==2018.06.15=====================
            #shutil.copy2(t_QtWebKit4_sou_path, t_QtWebKit4_des_path)
            ct.file().copy_file(t_QtWebKit4_sou_path, t_QtWebKit4_des_path)
            #===============骁颖==2018.06.15=====================
        except Exception,e:
            print e



def web_menu():
    hiero_right_plan.showWindow( hiero_right_view )  
def filter_menu():
    hiero_left_panle.showWindow( hiero_left_view )
    
    
    
    
    
if __name__=="__main__":
    start_before()
    hiero_right_key_menu = hiero_function( True )    
    hiero_right_view = right_ui( hiero_right_key_menu )
    hiero_right_plan = hiero.ui.windowManager()
    hiero_right_plan.addWindow(hiero_right_view)
    hiero_left_view  = left_ui()
    hiero_left_panle = hiero.ui.windowManager()
    hiero_left_panle.addWindow(hiero_left_view)
    hiero_left_view.sig_data.connect(hiero_right_key_menu.to_data)
    hiero_left_view.sig_data.connect(hiero_right_view.to_data)
    setWorkspace("cgtw")
    Menu             = hiero.ui.menuBar()
    cgteamwork_menu  = Menu.addMenu('Cgteamwork')
    open_filter      = QAction(QIcon(G_base_path+"/com_icon/logo.png"),'Open Filter',None)
    open_filter.triggered.connect( filter_menu )
    cgteamwork_menu.addAction( open_filter )
    open_web         = QAction(QIcon(G_base_path+"/com_icon/logo.png"),'Open Web',None)
    open_web.triggered.connect( web_menu )
    cgteamwork_menu.addAction( open_web )