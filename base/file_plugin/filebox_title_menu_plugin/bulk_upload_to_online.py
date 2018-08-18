# -*- coding: utf-8 -*-
"""
    Author:    黄骁颖
    Purpose:   批量上传到在线文件
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
from cgtw  import *
import ct
from   com_message_box   import *
import traceback

#排序
def __sorted(lis, is_reverse=False):  
    lists=list(lis)
    count=len(lists)
    for i in range(0,count):
        for j in range(i+1,count):
            if is_reverse:
                if unicode(lists[i]).lower() < unicode( lists[j]).lower():
                    lists[i],lists[j]=lists[j],lists[i]
            else:
                if unicode(lists[i]).lower() > unicode( lists[j]).lower():
                    lists[i],lists[j]=lists[j],lists[i]		
    return lists

#上传version
def upload_version(a_dict):
    web_path_lis=[]
    filename_lis=[]
    t_des_file_list=[]
    t_db=a_dict["db"]
    t_module=a_dict["module"]
    t_module_type=a_dict["module_type"]
    t_task_id=a_dict["task_id"]        
    t_old_des_file_list=a_dict["des_file_list"]
    t_title=a_dict["title"]
    t_version_id=a_dict["version_id"]
    t_server=a_dict["server"]
    t_tw=a_dict["tw"]
    for i in t_old_des_file_list:
        i=unicode(i).replace("\\", "/")
        filename_lis.append(os.path.basename(i))
        web_path_lis.append(unicode(i).replace( t_server , "/"))   
        t_des_file_list.append(i)
            
    return t_tw.con._send("c_version", "client_create", {"db":t_db, "id":t_version_id, "link_id":t_task_id, "sign":t_title,  "filename":filename_lis, "local_path":t_des_file_list, "web_path":web_path_lis })   



def change_to_regexp_list(file_rule_list):
    t_list=[]
    if isinstance(file_rule_list,list):
        for rule in file_rule_list:
            t_list.append(unicode(rule).strip().replace("#", "[0-9]").replace("?","[a-zA-Z]"))
        return t_list
    
def  filebox_bulk_upload_to_online():
    try:
        t_tw =tw()
        t_module      = t_tw.sys().get_sys_module()
        t_module_type = t_tw.sys().get_sys_module_type()
        t_db          = t_tw.sys().get_sys_database()
        task_id_list  = t_tw.sys().get_sys_id()
        t_filebox_id  =  t_tw.sys()._get_sys_key("filebox_id")
        t_is_all  =  t_tw.sys()._get_sys_key("is_all")
        
        res = t_tw.con._send("c_media_file","get_filebox_bulk_upload_data", {"db":t_db, "module":t_module, "module_type":t_module_type, "os":ct.com().get_os(), "filebox_id":t_filebox_id, "task_id_array":task_id_list})
        if isinstance(res, dict) and res.has_key("is_submit") and res.has_key("upload_to_server_action") and res.has_key("show_type") and res.has_key("filebox_data_list"):
            t_action            = 'upload'
            t_is_submit         = unicode(res["is_submit"]).lower()
            t_show_type         = unicode(res["show_type"]).lower()
            t_filebox_data_list = res["filebox_data_list"]
            temp_act            = res["upload_to_server_action"]
            if unicode(","+temp_act+",").find(",convert_before_upload,")!=-1:
                t_action="convert_movie_to_mp4"
                
            if unicode(","+temp_act+",").find(",convert_image_before_upload,")!=-1:
                t_action="convert_image_to_image"            
            
            if unicode(","+temp_act+",").find(",sequence_output_video,")!=-1:
                t_action="convert_seq_image_to_mov"
                
            #开始处理
            if isinstance(t_filebox_data_list, list):
                for t_dict_data in t_filebox_data_list:
                    if isinstance(t_dict_data, dict) and t_dict_data.has_key("path") and t_dict_data.has_key("server") and t_dict_data.has_key("rule") and t_dict_data.has_key("task_id") and t_dict_data.has_key("title") :
                        t_rule_list  = t_dict_data["rule"]
                        t_path       = t_dict_data["path"]  
                        t_server     = t_dict_data["server"]
                        t_task_id    = t_dict_data["task_id"]
                        t_title      = t_dict_data["title"]

                        t_version_id = ct.com().uuid()#随机生成的ID
                        re_list      = change_to_regexp_list(t_rule_list)
                        
                        #遍历本地文件排除histroy
                        if os.path.exists(t_path):
                            t_list = ct.file().get_path_list(t_path, re_list)
                            t_new_list=[]
                            for i in t_list:
                                if os.path.isdir(unicode(i)) and unicode(os.path.basename(i)).lower()=="history":
                                    continue
                                i = unicode(i).replace("\\","/")
                                t_new_list.append(i)
                            
                            if len(t_new_list)==0:
                                continue
                            
                            if isinstance(t_is_all, (str, unicode)) and unicode(t_is_all).strip().lower()!="y":
                                t_new_list = __sorted(t_new_list, True)
                                t_new_list=[t_new_list[0]]

                            
                            t_first = False
                            for i in t_new_list:
                                t_upload_list = [ {"sou":i,"des":unicode(i).replace(t_server, "/")} ]
                                if unicode(t_is_submit).strip().lower()=="y":
                                    
                                    if t_first == False:
                                        #上传verison
                                        if upload_version({"db":t_db, "module":t_module, "module_type":t_module_type, "task_id":t_task_id, "des_file_list": t_list, "title":t_title, "version_id":t_version_id, "server":t_server, "tw":t_tw})!=True:
                                            message().error(u"创建Version失败")
                                            return 
                                        #修改task表中的version_ID
                                        res =  t_tw.con._send("c_orm","update_version_id", {"id":t_task_id, "db":t_db, "module":t_module, "module_type":t_module_type, "version_id":t_version_id})
                                        if res != True:
                                            return                                             
                                        t_first = True
           
                                file_name = os.path.basename(t_upload_list[0]["sou"])     
                                t_dic={'name':file_name, 'task': [{"action":t_action, 
                                                                   "is_contine":True, 
                                                                   "data_list":t_upload_list, 
                                                                   "db":t_db, 
                                                                   "module":t_module, 
                                                                   "module_type":t_module_type, 
                                                                   "task_id":t_task_id, 
                                                                   "version_id":t_version_id}
                                                                  ]}
                                #print t_dic["name"] +u' --> send to queue'
                                t_tw.local_con._send("queue_widget","add_task", {"task_data":t_dic}, "send")                                  
 


        
    except Exception,e:
        ct.log().add(traceback.format_exc(), __file__)
        message().error(u"(bulk_upload_to_online)上传失败:\n"+e.message)
    else:
        #message().info(u"已发送到队列处理")
        t_tw.local_con._send("queue_widget","show", {}, "send")
    
if __name__=="__main__":
    filebox_bulk_upload_to_online()