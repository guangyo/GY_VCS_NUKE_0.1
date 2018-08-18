#coding:utf8
#Author:Yasuo Wang
#Time  :2017-12-29
#Describe:New finishing,数据量过大
#         CgTeamWork V5整合
import re
import os
import sys
import time
import json
import shutil
import socket
import datetime
G_base_path = os.path.dirname( os.path.dirname( __file__.replace("\\","/") ) )
G_com_path  = G_base_path + "/com_lib/"
G_cgtw_path = os.path.dirname( G_base_path ) + "/cgtw/"
if not G_base_path in sys.path:
    sys.path.append( G_base_path )
if not G_com_path in sys.path:
    sys.path.append( G_com_path )
if not G_cgtw_path in sys.path:
    sys.path.append( G_cgtw_path )
import ct
from   com_work_log    import *
from   com_message_box import *
from   cgtw            import *
def connect_to_hiero_menu(t_tw, t_database, t_id_list):
    t_new_list = []
    t_module   = t_tw.sys().get_sys_module()
    t_module_type   = t_tw.sys().get_sys_module_type()
    if  t_module!="shot" or t_module_type!="task":
        message().error(u"此插件只能在shot_task模块使用!")
    try:
        datalist = t_tw.task_module(t_database,t_module,t_id_list).get(["eps.id","shot.id","task.id","shot.shot","task.submit_file_path"])
    except:
        datalist = False
    if datalist==False or datalist==[] or datalist=="":
        message().error(u"读取数据库失败!")
    for data in datalist:
        json_database  = t_database
        json_eps_id    = data["eps.id"]
        json_shot_id   = data["shot.id"]
        json_task_id   = data["task.id"]
        json_path      = data["task.submit_file_path"]
        json_shot      = data["shot.shot"]
        if json_path==None or json_path=="":
            pass
        else:
            data_file_json = json.loads(json_path)
            if data_file_json.has_key("path"):
                for t_path in data_file_json["path"]:
                    t_new_list.append([json_database, json_eps_id, json_shot_id, json_task_id, t_path,json_shot ])
            elif data_file_json.has_key("file_path"):
                t_data = file_path_to_path( data_file_json["file_path"] )  
                for t_path in t_data:
                    t_new_list.append([ json_database, json_eps_id, json_shot_id, json_task_id, t_path,json_shot ])
    t_json_dict = {"video_list":t_new_list,"database":t_database}
    sen_message(t_json_dict)
def connect_to_hiero_file_box(t_tw, t_database, t_id_list):
    t_new_list=[]
    t_module=t_tw.sys().get_sys_module()
    t_module_type   = t_tw.sys().get_sys_module_type()
    if  t_module!="shot" or t_module_type!="task":
        message().error(u"此插件只能在shot_task模块使用!")
    t_slt_path=t_tw.sys().get_sys_file()
    if t_slt_path==[] or t_slt_path=="" or t_slt_path==False:
        message().error(u"请选择文件!")
    try:
        datalist = t_tw.task_module(t_database,t_module,t_id_list).get(["eps.id","shot.id","task.id","shot.shot"])
    except:
        datalist = False
    if len(datalist)!=1 or datalist==False:
        message().error(u"读取数据库失败!")
    for path in t_slt_path:
        json_database=t_database
        json_eps_id=datalist[0]["eps.id"]
        json_shot_id=datalist[0]["shot.id"]
        json_task_id=datalist[0]["task.id"]
        json_shot=datalist[0]["shot.shot"]
        t_new_list.append([json_database,json_eps_id,json_shot_id,json_task_id,path,json_shot])
    t_json_dict = {"video_list":t_new_list, "database":t_database}
    sen_message(t_json_dict)
def file_path_to_path(self,file_path_list):
    path_list=[]
    for file_path in file_path_list:
        if os.path.isfile(file_path.replace("\\","/")) and not os.path.splitext(file_path)[-1] in [".mov",".avi",".mp4",".3gp",".rmvb"]:
            a_path = os.path.dirname(file_path)
        else:
            a_path = file_path.replace("\\","/")
        if not a_path.replace("\\","/") in path_list:
            path_list.append( a_path.replace("\\","/") )
    return path_list
def sen_message(a_message):
    t_data  = "@start@" + json.dumps(a_message) + "@end@"
    t_list  = re.findall(r'.{1024}',t_data)
    if len(t_data)!=len(''.join(t_list)):
        t_list.append( t_data[len(''.join(t_list)):] )
    for i in t_list:
        send_data( i )
def send_data( a_data ):
    try:
        click_send = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        click_send.connect(("127.0.0.1", 8090))
        click_send.send( a_data )
        data = click_send.recv(1024)
        if data == "False":
            click_send.close()
            message().error(u"插件执行失败!")
        elif data == "True":
            click_send.close()
            message().info(u"完成!")    
        else:
            click_send.close()
    except Exception,e:
        message().error(u"Hiero_filter插件未运行!")
        return
        

    
            
if __name__=="__main__":
    try:
        t_tw    = tw()
        action  = t_tw.sys().get_argv_key("action")
        if action == False or unicode(action).strip() == "":
            message().error(u"插件action配置错误")
        t_database = t_tw.sys().get_sys_database()
        t_id_list  = t_tw.sys().get_sys_id()
        if   action == "menu":
            connect_to_hiero_menu(    t_tw, t_database, t_id_list)
        elif action == "file_box":
            connect_to_hiero_file_box(t_tw, t_database, t_id_list)
        else:
            message().error(u"参数配置错误!")
    except:
        message().error(u"插件执行失败!")
