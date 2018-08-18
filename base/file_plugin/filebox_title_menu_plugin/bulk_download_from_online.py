# -*- coding: utf-8 -*-
"""
    Author:    黄骁颖
    Purpose:   从在线文件批量下载
    Created:   2018-4-11
"""
import os,sys
G_base_path =  os.path.dirname(os.path.dirname( os.path.dirname( __file__.replace("\\","/") ) ))
G_cgtw_path = os.path.dirname( G_base_path ) + "/cgtw/"
G_com_lib_path = G_base_path + "/com_lib/"

if not G_com_lib_path in sys.path:
    sys.path.append( G_com_lib_path )
    
if not G_base_path in sys.path:
    sys.path.append( G_base_path )
if not G_cgtw_path in sys.path:
    sys.path.append( G_cgtw_path )
import traceback
from cgtw  import *
import ct
from   com_message_box   import *
def  filebox_bulk_download_from_online():
    try:
        t_tw =tw()
        t_module      = t_tw.sys().get_sys_module()
        t_module_type = t_tw.sys().get_sys_module_type()
        t_db          = t_tw.sys().get_sys_database()
        task_id_list  = t_tw.sys().get_sys_id()
        t_filebox_id  =  t_tw.sys()._get_sys_key("filebox_id")
        t_is_all  =  t_tw.sys()._get_sys_key("is_all")
        
        res =t_tw.con._send("c_media_file","get_filebox_bulk_download_data", {"db":t_db, "module":t_module, "module_type":t_module_type, "os":ct.com().get_os(), "is_all":t_is_all, "filebox_id":t_filebox_id, "task_id_array":task_id_list})
        for dic in res:
            t_current_folder_id=dic["current_folder_id"]
            t_data_list=dic["data_list"]
            t_filebox_data=dic["filebox_data"]
        
            t_des_dir=dic["des_dir"]
            if isinstance(t_data_list, list):
                for t_dict_data in t_data_list:
                    if isinstance(t_dict_data, dict) and t_dict_data.has_key("id") and t_dict_data.has_key("name") and t_dict_data.has_key("is_folder"):
                        #print t_dict_data["name"]+u' --> send to queue'
                        t_task_data={'name':t_dict_data["name"], 'task': [{"action":"download", "is_contine":True, "data_list":[t_dict_data], "db":t_db, "des_dir":t_des_dir, "filebox_data":t_filebox_data,"current_folder_id":t_current_folder_id}]} 
                        t_tw.local_con._send("queue_widget","add_task", {"task_data":t_task_data}, "send")    

    except Exception,e:
        ct.log().add(traceback.format_exc(), __file__)
        message().error(u"(bulk_download_from_online)下载失败:\n"+e.message)
    else:
        #message().info(u"已发送到队列处理")
        t_tw.local_con._send("queue_widget","show", {}, "send")
if __name__=="__main__":
    filebox_bulk_download_from_online()