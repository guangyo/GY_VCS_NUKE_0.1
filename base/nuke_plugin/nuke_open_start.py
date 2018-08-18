#coding:utf8
#Author:王晨飞
#Time  :2018-1-2
#Describe:CgTeamWork V5整合
#         启动方式:   "C:/Program Files/Nuke10.5v4/Nuke10.5.exe D:/CgTeamWork/cgteamwork_v5/bin/base/nuke_plugin/nuke_open_start.py"
#         添加右侧面板启动方式（传入database, module, id）
#                             正常启动sys.argv   [plugin_path]
#                             参数启动sys.argv   [plugin_path, database, module, [id]]
#         初始化点击select task
#         root 状态修复
import os
import sys
G_NukePlugin_Path = os.path.dirname( sys.argv[0] )
sys.path.append( G_NukePlugin_Path )
from nuke_open_plugin import *
t_panel = Nuke_Panel()
