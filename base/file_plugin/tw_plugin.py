# -*- coding: utf-8 -*-
#Author:王晨飞
#Time  :2017-12-29
#Describe:全部都放到子线程内进行
#         宽高
#         是否覆盖
#         CgTeamWork V5整合
import os
import sys
import time
import json
import shutil
import datetime
import traceback
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
from   com_message_box import *
from   com_work_log    import *
from   com_function    import * 
from   cgtw            import *
def drag_image_get_thumbnail(a_data, a_queue, a_signal, a_event):
    """
    文件筐插件,拖入图片/右键选择图片(可以选择/拖入文件夹):
    1:  allow_format,    允许格式           ex: .png|.tif   key可以不填写  
    2:  ban_format,      禁止格式           ex: .jpg|.dpx   key可以不填写  
    3:  image_sign,      生成缩略图字段标识  ex: shot.image  key可以不填写,默认为task.image
    4:  des_file_sign    拷贝到目标目录标识  ex: maya_work   key可以不填写  
    5:  is_show_log      是否显示工作日志    ex: Y/N         key可以不填写
    6:  is_get_folder    是否查询目录内的图片ex: Y/N         key可以不填写  
    """
    INFO_FIELD_SIGN=1#信息模块标识
    TASK_FIELD_SIGN=2#制作模块标识
    
    t_tw              = a_data[0]
    t_databse         = a_data[1]
    t_id_list         = a_data[2]

    k_allow_format    = t_tw.sys().get_argv_key( "allow_format" )#允许格式
    k_ban_format      = t_tw.sys().get_argv_key( "ban_format" )#禁止格式
    k_image_sign      = t_tw.sys().get_argv_key( "image_sign" )#生成缩略图字段标识
    k_des_file_sign   = t_tw.sys().get_argv_key( "des_file_sign" )#拷贝到目标目录标识
    k_is_get_folder   = t_tw.sys().get_argv_key( "is_get_folder" )#是否要查询目录内的图片
    
    t_drag_file_list  = t_tw.sys().get_sys_file()
    t_module          = t_tw.sys().get_sys_module()
    t_module_type     = t_tw.sys().get_sys_module_type()
    #------模块处理
    if t_module_type!="task":
        t_tw.sys().set_return_data()
        a_signal.emit("error", u"仅允许在 (task) 模块使用本插件!", True)
        a_event.wait()
    #------配置缩略图字段标识处理 
    t_image_sign_type = TASK_FIELD_SIGN
    t_image_sign      = "task.image"#默认为制作的缩略图
    
    if k_image_sign!=False and str(k_image_sign).strip()!="":
        if len( k_image_sign.split(".") ) == 2:
            if k_image_sign.split(".")[0] == "task":
                t_image_sign_type = TASK_FIELD_SIGN
                t_image_sign      = k_image_sign
            elif k_image_sign.split(".")[0] == t_module:
                t_image_sign_type = INFO_FIELD_SIGN
                t_image_sign      = k_image_sign
            else:
                t_tw.sys().set_return_data()
                a_signal.emit("error", u"需要更新的缩略图字段标识错误!", True)
                a_event.wait()                
        else:
            t_tw.sys().set_return_data()
            a_signal.emit("error", u"需要更新的缩略图字段标识错误!", True)
            a_event.wait()  


    #------允许格式处理
    t_allow_format = False
    if k_allow_format!=False and str(k_allow_format).strip()!="":
        t_allow_format = k_allow_format.split("|")
        a_signal.emit("log", u"Info:将允许以下文件格式生成缩略图:" + k_allow_format, True)
    #------禁止格式处理
    t_ban_format = False
    if k_ban_format!=False   and str(k_ban_format).strip()!="":
        t_ban_format   = k_ban_format.split("|")
        a_signal.emit("log", u"Info:将禁止以下文件格式生成缩略图:" + k_ban_format, True )
    #------获取文件list处理
    if k_is_get_folder!=False and unicode( k_is_get_folder ).lower() == "y":
        t_new_list = []
        for i in t_drag_file_list:
            if os.path.isdir(i):
                lists = []
                for i in ct.file().get_path_list( i ):
                    if i.strip().lower().find("thumbs.db")==-1 and i.strip().lower().find(".ini")==-1:
                        lists.append( i )
                if len(lists)>0:
                    t_new_list.append( lists[0] )
            else:
                t_new_list.append( i )
    else:
        t_new_list = t_drag_file_list
    #------处理需要生成的缩略图的文件格式
    t_image_list = []
    if t_allow_format!=False:
        a_signal.emit( "log", u"Info:将允许以下文件生成缩略图:", True)
        for temp in t_new_list:
            if os.path.isfile( temp.replace("\\","/") ) and os.path.splitext( temp.replace("\\","/") )[-1] in t_allow_format:
                t_image_list.append( temp.replace("\\","/") )
                a_signal.emit( "log", temp.replace("\\","/"),  True)
                
    else:
        if t_ban_format!=False:
            a_signal.emit("log", u"Info:将允许以下文件生成缩略图:", True)
            for temp in t_new_list:
                if os.path.isfile( temp.replace("\\","/") ) and not os.path.splitext( temp.replace("\\","/") )[-1] in t_ban_format:
                    t_image_list.append( temp.replace("\\","/") ) 
                    a_signal.emit("log", temp.replace("\\","/"), True )
        else:
            t_image_list = t_new_list
            a_signal.emit("log", u"Info:将允许所有文件生成缩略图!", True)
    #-----开始生成缩略图
    a_signal.emit("log", u"Info:开始生成缩略图!", True)
    if t_image_sign_type == TASK_FIELD_SIGN :
        try:
            t_tw.task_module(t_databse, t_module, t_id_list).set_image( t_image_sign, t_image_list )
            a_signal.emit("log",  u"Success:生成缩略图成功!", True)
        except Exception,e:
            a_signal.emit("log",  u"Error:生成缩略图失败!", True)
            t_tw.sys().set_return_data()
            a_signal.emit("error", u"生成缩略图失败!", True)
            a_event.wait()
    elif t_image_sign_type == INFO_FIELD_SIGN :
        try:
            t_info_id = t_tw.task_module(t_databse, t_module, t_id_list).get( [t_module + ".id"] )[0][ t_module + ".id" ]
            t_tw.info_module(t_databse, t_module, [t_info_id] ).set_image( t_image_sign, t_image_list )
            a_signal.emit("log",  u"Success:生成缩略图成功!", True)
        except Exception,e:
            a_signal.emit("log",  u"Error:生成缩略图失败!", True)
            t_tw.sys().set_return_data()
            a_signal.emit("error", u"生成缩略图失败!", True)
            a_event.wait()
    #------拷贝文件
    t_fail_str = ''
    if k_des_file_sign!=False   and str(k_des_file_sign).strip()!="":
        a_signal.emit("log",  u"Info:开始拷贝文件!",True)
        try:
            t_des_path = t_tw.task_module(t_databse, t_module, t_id_list).get_dir( [k_des_file_sign] )[0][k_des_file_sign]
        except Exception,e:
            a_signal.emit("log",  u"Error:读取目标目录失败!", True)
            t_tw.sys().set_return_data()
            a_signal.emit("error", u"读取目标目录失败!", True)
            a_event.wait()
        t_fail_str = com_copy(t_drag_file_list, t_des_path, a_work_log_signal = a_signal, a_fail_str = t_fail_str, a_is_folder_son=True)
        a_signal.emit("log", u"Info:拷贝文件结束!", True)
    if t_fail_str != "":
        t_tw.sys().set_return_data()
        a_signal.emit("error", u'拷贝失败:\n' + t_fail_str, True)
        a_event.wait()
    else:
        a_signal.emit("close","",True)
        a_event.wait()   
def drag_mov_get_thumbnail(a_data, a_queue, a_signal, a_event):
    """
    文件筐插件,拖入mov/右键mov(可以选择/拖入文件夹):
    1:  is_get_thumbnail, 是否获取缩略图      ex: Y/N          key可以不填写
    2:  is_update_frame, 是否更新帧数         ex: Y/N          key可以不填写
    3:  is_check_frame,  是够检查帧数         ex: Y/N          key可以不填写
    4:  is_get_folder,   是否查询目录里的文件         ex: Y/N   key可以不填写
    5:  image_sign,      生成缩略图字段标识   ex: shot.image    key可以不填写,默认为task.image
    6:  des_file_sign,   拷贝到目标目录标识   ex: maya_work     key可以不填写
    7:  is_show_log,     是否显示工作日志     ex: Y/N           key可以不填写
    8： frame_rate,      帧率                ex:24             key可以不填写
    9:  width            宽                                    key可以不填写
    10: height           高                                    key可以不填写
    """
    t_tw              = a_data[0]
    t_databse         = a_data[1]
    t_id_list         = a_data[2]
    
    INFO_FIELD_SIGN=1#信息模块标识
    TASK_FIELD_SIGN=2#制作模块标识    
    
    k_is_get_thumanil = t_tw.sys().get_argv_key( "is_get_thumbnail" )
    k_is_update_frame = t_tw.sys().get_argv_key( "is_update_frame" )
    k_is_check_frame  = t_tw.sys().get_argv_key( "is_check_frame" )
    k_is_get_folder   = t_tw.sys().get_argv_key( "is_get_folder" )
    k_image_sign      = t_tw.sys().get_argv_key( "image_sign" )
    k_des_file_sign   = t_tw.sys().get_argv_key( "des_file_sign" )
    k_frame_rate      = t_tw.sys().get_argv_key( "frame_rate" )
    k_width           = t_tw.sys().get_argv_key( "width" )
    k_height          = t_tw.sys().get_argv_key( "height" )
    
    t_drag_file_list  = t_tw.sys().get_sys_file()
    t_module          = t_tw.sys().get_sys_module()    
    t_module_type     = t_tw.sys().get_sys_module_type()
    #------模块处理
    if t_module_type!="task":
        t_tw.sys().set_return_data()
        a_signal.emit("error", u"仅允许在 (task) 模块使用本插件!", True)
        a_event.wait()
    #------获取文件list处理
    if k_is_get_folder!=False and unicode( k_is_get_folder ).lower() == "y":
        t_new_list = []
        for i in t_drag_file_list:
            if os.path.isdir(i):
                t_new_list = t_new_list + ct.file().get_path_list( i )
            else:
                t_new_list.append( i )
    else:
        t_new_list = t_drag_file_list
    
    #------获取所有视频的帧数list,及视频list
    t_frame_list     = []
    t_thumanil_list  = []
    t_avi_info_dict  = False
    for i in t_new_list:
        if os.path.isfile( i ):
            try:
                t_avi_info = ct.mov().get_avi_info( i )
                t_fate     = t_avi_info["FrameRate"]
                t_frame_list.append( t_avi_info["FrameCount"] )
                t_avi_thumanil = ct.com().get_tmp_path() + "/" + ct.com().uuid() +".png"
                ct.mov().get_mov_thumbnail(i, t_avi_thumanil.replace("\\","/") )
                t_thumanil_list.append( t_avi_thumanil.replace("\\","/") )
                t_avi_info_dict = t_avi_info
            except Exception,e:
                pass
    #------检查宽高
    try:
        if str( k_width ).strip() !='' and  k_width!=False:
            if t_avi_info_dict!=False and t_avi_info_dict.has_key("Width"):
                if int(k_width)!=int(t_avi_info_dict["Width"]):
                    t_tw.sys().set_return_data()
                    a_signal.emit("error", u"分辨率不正确!", True)
                    a_event.wait()                   
            else:
                t_tw.sys().set_return_data()
                a_signal.emit("error", u"分辨率不正确!", True)
                a_event.wait()               
        if str( k_height ).strip() !='' and  k_height!=False:
            if t_avi_info_dict!=False and t_avi_info_dict.has_key("Height"):
                if int(k_height)!=int(t_avi_info_dict["Height"]):
                    t_tw.sys().set_return_data()
                    a_signal.emit("error", u"分辨率不正确!", True)
                    a_event.wait()       
            else:
                t_tw.sys().set_return_data()
                a_signal.emit("error", u"分辨率不正确!", True)
                a_event.wait()   
    except Exception,e:
        t_tw.sys().set_return_data()
        a_signal.emit("error", u"分辨率不正确!", True)
        a_event.wait()          
    #------检查帧率
    if str( k_frame_rate ).strip() !='' and  k_frame_rate!=False:
        try:
            if int(k_frame_rate)!=int(float(t_fate)):
                t_tw.sys().set_return_data()
                a_signal.emit("error", u"帧率不正确!", True)
                a_event.wait()                
        except Exception,e:
            t_tw.sys().set_return_data()
            a_signal.emit("error", u"帧率不正确!", True)
            a_event.wait()
    #------是否检查帧数
    if str( k_is_check_frame ).lower() == "y":
        t_frame_number = 0
        for i in t_frame_list:
            t_frame_number = t_frame_number + int(i)
        a_signal.emit("log", u"Info:提交视频帧数为%s"%(unicode(t_frame_number)), True)
        try:
            t_info_id = t_tw.task_module(t_databse, t_module, t_id_list).get( [t_module + ".id"] )[0][ t_module + ".id" ]
            t_frmaes  = t_tw.info_module(t_database, "shot", [t_info_id] ).get(["shot.frame"])[0]["shot.frame"]
            if t_frmaes == "None" or t_frmaes == False or t_frmaes == "" or t_frmaes == None:
                t_frmaes = 0
            a_signal.emit("log", u"Info:系统帧数为%s"%(unicode(t_frmaes)), True)
            if int(t_frame_number)!=int(t_frmaes):
                if str( k_is_update_frame ).lower() == "y":
                    a_signal.emit("question", u"----系统帧数----提交文件总帧数----\n----%s----%s----\n是否更新帧数?"%(unicode(t_frmaes),unicode(t_frame_number)), True)
                    a_event.wait()
                    t_queue = a_queue.get()
                    if t_queue=="Y":
                        t_tw.info_module(t_database, "shot", [t_info_id] ).set({"shot.frame":t_frame_number})
                        a_signal.emit("log", u"Success:更新帧数成功!", True)
                    else:
                        t_tw.sys().set_return_data()
                        a_signal.emit("close","",True)
                        a_event.wait()                         
                else:
                    a_signal.emit("question", u"----系统帧数----提交文件总帧数----\n----%s----%s----\n是否继续后续操作?"%(unicode(t_frmaes),unicode(t_frame_number)), True)
                    a_event.wait()
                    t_queue = a_queue.get()                  
                    if t_queue=="N":
                        t_tw.sys().set_return_data()
                        a_signal.emit("close","",True)
                        a_event.wait()   
            else:
                a_signal.emit("log", u"Info:帧数正确!", True)
        except Exception,e:
            a_signal.emit("log", u"Error:检查/更新帧数,发生未知错误!", True)
            t_tw.sys().set_return_data()
            a_signal.emit("error", u"检查/更新帧数,发生未知错误!", True)
            a_event.wait()            
                        
    else:
        #------是否更新帧数
        if str( k_is_update_frame ).lower() == "y":
            try:
                t_frame_number = 0
                for i in t_frame_list:
                    t_frame_number = t_frame_number + int(i)
                a_signal.emit("log", u"Info:提交视频帧数为:%s"%(unicode(t_frame_number)), True)
                t_info_id = t_tw.task_module(t_databse, t_module, t_id_list).get( [t_module + ".id"] )[0][ t_module + ".id" ]
                t_tw.info_module(t_database, "shot", [t_info_id] ).set({"shot.frame":t_frame_number})
                a_signal.emit("log", u"Success:更新帧数成功!", True)
            except Exception,e:
                a_signal.emit("log", u"Error:更新帧数,发生未知错误!", True)
                t_tw.sys().set_return_data() 
                a_signal.emit("error", u"更新帧数,发生未知错误!", True)
                a_event.wait()                
    #------是够更新缩略图
    if str( k_is_get_thumanil ).lower() == "y":
        
        #------配置缩略图字段标识处理 
        t_image_sign_type = TASK_FIELD_SIGN
        t_image_sign      = "task.image"#默认为制作的缩略图
        
        if k_image_sign!=False and str(k_image_sign).strip()!="":
            if len( k_image_sign.split(".") ) == 2:
                if k_image_sign.split(".")[0] == "task":
                    t_image_sign_type = TASK_FIELD_SIGN
                    t_image_sign      = k_image_sign
                elif k_image_sign.split(".")[0] == t_module:
                    t_image_sign_type = INFO_FIELD_SIGN
                    t_image_sign      = k_image_sign
                else:
                    t_tw.sys().set_return_data()
                    a_signal.emit("error", u"需要更新的缩略图字段标识错误!", True)
                    a_event.wait()                
            else:
                t_tw.sys().set_return_data()
                a_signal.emit("error", u"需要更新的缩略图字段标识错误!", True)
                a_event.wait()  
                
        #-----开始生成缩略图
        a_signal.emit("log",  u"Info:开始生成缩略图!", True)
        if t_image_sign_type == TASK_FIELD_SIGN :
            try:
                t_tw.task_module(t_databse, t_module, t_id_list).set_image( t_image_sign, t_thumanil_list )
                a_signal.emit("log",  u"Success:生成缩略图成功!", True)
            except Exception,e:
                a_signal.emit("log",  u"Error:生成缩略图失败!", True)
                t_tw.sys().set_return_data()
                a_signal.emit("error", u"生成缩略图失败!", True)
                a_event.wait()                
        elif t_image_sign_type == INFO_FIELD_SIGN :
            try:
                t_info_id = t_tw.task_module(t_databse, t_module, t_id_list).get( [t_module + ".id"] )[0][ t_module + ".id" ]
                t_tw.info_module(t_databse, t_module, [t_info_id] ).set_image( t_image_sign, t_thumanil_list )
                a_signal.emit("log",  u"Success:生成缩略图成功!", True)
            except Exception,e:
                a_signal.emit("log",  u"Error:生成缩略图失败!", True)
                t_tw.sys().set_return_data()
                a_signal.emit("error", u"生成缩略图失败!", True)
                a_event.wait()                
    #------是否拷贝文件
    t_fail_str = ''
    if k_des_file_sign!=False   and str(k_des_file_sign).strip()!="" and str(k_des_file_sign).strip()=="None":
        a_signal.emit("log",  u"Info:开始拷贝文件!", True)
        try:
            t_des_path = t_tw.task_module(t_databse, t_module, t_id_list).get_dir( [k_des_file_sign] )[0][k_des_file_sign]
        except Exception,e:
            a_signal.emit("log",  u"Error:读取目标目录失败!", True)
            t_tw.sys().set_return_data()
            a_signal.emit("error", u"读取目标目录失败!", True)
            a_event.wait()            
        #-------------------------
        t_fail_str = com_copy(t_drag_file_list, t_des_path, a_work_log_signal = a_signal, a_fail_str = t_fail_str,  a_is_folder_son=True)
        #-------------------------         
        a_signal.emit("log",  u"Info:拷贝文件结束!", True)
    if t_fail_str != "":
        t_tw.sys().set_return_data()
        a_signal.emit("error", u'拷贝失败:\n' + t_fail_str, True)
        a_event.wait()        
    else:
        a_signal.emit("close","",True)
        a_event.wait()   




#---------------------------------------------------------------------------骁颖------------------------------------------------------------------------ 
def __com_copy_sou_path_to_des_path(a_dict, a_queue, a_signal, a_event):

    t_tw              = a_dict['tw']
    t_database        = a_dict['db']
    t_id_list         = a_dict['id_list']
    t_module          = a_dict['module']
    k_sou_type        = a_dict['sou_type']
    k_des_type        = a_dict['des_type']
    k_sou             = a_dict['sou']
    k_des             = a_dict['des']   
    k_add_str         = a_dict['add_str']
    k_replace_str     = a_dict["replace_str" ]
    k_is_cover        = a_dict[ "is_cover" ]
    k_is_copy_all     = a_dict[ "is_copy_all"]
    

    if str(k_is_cover).lower()=="y":
        is_cover = True
    else:
        is_cover = False
    t_time       = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    if str(k_add_str).strip()=='' or k_add_str==False:
        k_add_str=False
    if str(k_replace_str).strip()=='' or k_replace_str==False:
        k_replace_str=False
    
    
    if k_is_copy_all==False or str(k_is_copy_all).strip().lower()=='y':
        k_is_copy_all="Y"
    else:
        k_is_copy_all="N"
    
        
    try:
        if str( k_sou_type ) == "select" and str( k_des_type ) == "select":#文件筐拖入文件/文件筐右键选择文件 ---> 所选路径下

            t_sou_list = t_tw.sys().get_sys_file()
            a_signal.emit(u"QFileDialog",u"选择目录",True)
            a_event.wait()
            t_des_path = a_queue.get()
            if t_des_path == "":
                a_signal.emit("close","",True)
                a_event.wait() 
            t_fail_str = ''
            
            t_fail_str = com_copy(t_sou_list, t_des_path, a_is_cover = is_cover, a_add_str = k_add_str, a_replace_str = k_replace_str, a_work_log_signal = a_signal, a_fail_str = t_fail_str, a_is_folder_son = True, a_time=t_time, a_is_copy_all = k_is_copy_all)

            if t_fail_str != "":
                t_tw.sys().set_return_data()
                a_signal.emit("error",u'拷贝失败:\n' + t_fail_str, True)
                a_event.wait()                
            else:
                a_signal.emit("info",u"完成", True)
                time.sleep(0.01)
                a_event.wait()
            a_signal.emit("close","",True)
            a_event.wait()            
        elif str( k_sou_type ) == "select" and str( k_des_type ) == "sign":#文件筐拖入文件/文件筐右键选择文件 ---> 目录标识下
            
            t_sou_list = t_tw.sys().get_sys_file()
            try:
                t_des_path = t_tw.task_module(t_database, t_module, t_id_list).get_dir([k_des])[0][k_des]
            except:
                a_signal.emit("error",u'取目录标识失败', True)
                a_event.wait()                   
            t_fail_str = ''
            t_fail_str = com_copy(t_sou_list, t_des_path,a_is_cover = is_cover, a_add_str = k_add_str, a_replace_str = k_replace_str, a_work_log_signal = a_signal, a_fail_str = t_fail_str, a_is_folder_son = True, a_time=t_time, a_is_copy_all = k_is_copy_all)
            if t_fail_str != "":
                t_tw.sys().set_return_data()
                a_signal.emit("error",u'拷贝失败:\n' + t_fail_str, True)
                a_event.wait()                      
            else:
                a_signal.emit("info",u"完成", True)
                time.sleep(0.01)
                a_event.wait()
            a_signal.emit("close","",True)
            a_event.wait()             
        elif str( k_sou_type ) == "sign" and str( k_des_type ) == "select":#文件筐拖入时获取sign/目录右键执行获取sign/流程插件 ---> 所选路径下
            t_sou_list = []
            try:
                t_data     = t_tw.task_module(t_database, t_module, t_id_list).get_dir([k_sou])
            except:
                a_signal.emit("error",u'取目录标识失败', True)
                a_event.wait()                   
            for data in t_data:
                t_sou_list.append( data[k_sou] )
            a_signal.emit(u"QFileDialog",u"选择目录",True)
            a_event.wait()
            t_des_path = a_queue.get()
            if t_des_path == "":
                a_signal.emit("close","",True)
                a_event.wait()
            t_fail_str = ''
            t_fail_str = com_copy(t_sou_list, t_des_path, a_is_cover = is_cover,a_add_str = k_add_str, a_replace_str = k_replace_str, a_work_log_signal = a_signal, a_fail_str = t_fail_str, a_time=t_time, a_is_copy_all = k_is_copy_all)
            if t_fail_str != "":
                t_tw.sys().set_return_data()
                a_signal.emit("error",u'拷贝失败:\n' + t_fail_str, True)
                a_event.wait()                      
            else:
                a_signal.emit("info",u"完成", True)
                time.sleep(0.01)
                a_event.wait()
            a_signal.emit("close","",True)
            a_event.wait()          
        elif str( k_sou_type ) == "sign" and str( k_des_type ) == "sign":#文件筐拖入时获取sign/目录右键执行获取sign/流程插件 ---> 目录标识下
            t_sou_list = []
            t_des_list = []
            try:
                t_data     = t_tw.task_module(t_database, t_module, t_id_list).get_dir([k_sou,k_des])
            except :
                a_signal.emit("error",u'取目录标识失败', True)
                a_event.wait()                   
            for data in t_data:
                t_sou_list.append( data[k_sou] )
                t_des_list.append( data[k_des] )
            t_fail_str = ''
            t_fail_str = com_copy(t_sou_list, t_des_list, a_is_cover = is_cover,a_add_str = k_add_str,a_replace_str = k_replace_str, a_work_log_signal = a_signal, a_fail_str = t_fail_str, a_time=t_time, a_is_copy_all = k_is_copy_all)
            if t_fail_str != "":
                t_tw.sys().set_return_data()
                a_signal.emit("error",u'拷贝失败:\n' + t_fail_str, True)
                a_event.wait()
            else:
                a_signal.emit("info",u"完成", True)
                time.sleep(0.01)
                a_event.wait()
            a_signal.emit("close","",True)
            a_event.wait()               
        elif str( k_sou_type ) == "check" and str( k_des_type ) == "select":#文件筐拖入时获取check/目录右键执行获取check/流程插件 ---> 所选路径下
            t_sou_list    = []
            t_fail_str    = ''
            t_submit_sign = "task.submit_file_path"
            try:
                t_data        = t_tw.task_module(t_database, t_module, t_id_list).get( [t_submit_sign] )    
            except :
                a_signal.emit("error",u'取数据失败', True)
                a_event.wait()                   
            for data in t_data:
                temp = data[t_submit_sign]
                if temp is not None and len(temp)>4:
                    file_json = json.loads(temp)
                    if file_json.has_key("path"):
                        path_list = file_json['path']
                    elif file_json.has_key("file_path"):
                        path_list = file_json['file_path']
                    else:
                        path_list = []
                else:
                    path_list = []
                t_sou_list =  t_sou_list + path_list
                
            a_signal.emit(u"QFileDialog",u"选择目录",True)
            a_event.wait()
            t_des_path = a_queue.get()
            if t_des_path == "":
                a_signal.emit("close","",True)
                a_event.wait()   
            t_fail_str = com_copy(t_sou_list, t_des_path, a_is_cover = is_cover,a_add_str = k_add_str, a_replace_str = k_replace_str, a_work_log_signal = a_signal, a_fail_str = t_fail_str, a_is_folder_son = True, a_time=t_time, a_is_copy_all = k_is_copy_all)
            if t_fail_str != "":
                t_tw.sys().set_return_data()
                a_signal.emit("error",u'拷贝失败:\n' + t_fail_str, True)
                a_event.wait()
            else:
                a_signal.emit("info",u"完成", True)
                time.sleep(0.01)
                a_event.wait()
            a_signal.emit("close","",True)
            a_event.wait()   
        elif str( k_sou_type ) == "check" and str( k_des_type ) == "sign":#文件筐拖入时获取check/目录右键执行获取check/流程插件 ---> 目录标识下
            t_fail_str = ''
            t_submit_sign = "task.submit_file_path"
            try:
                t_data        = t_tw.task_module(t_database, t_module, t_id_list).get_field_and_dir( [t_submit_sign], [k_des] )
            except :
                a_signal.emit("error",u'取数据失败', True)
                a_event.wait()     
                
            for data in t_data:
                temp = data[t_submit_sign]
                if temp is not None and len(temp)>4:
                    file_json = json.loads(temp)
                    if file_json.has_key("path"):
                        path_list = file_json['path']
                    elif file_json.has_key("file_path"):
                        path_list = file_json['file_path']
                    else:
                        path_list = []
                else:
                    path_list = []
                        
                t_fail_str = com_copy(path_list, data[k_des], a_is_cover = is_cover,a_add_str = k_add_str, a_replace_str = k_replace_str, a_work_log_signal = a_signal, a_fail_str = t_fail_str, a_is_folder_son = True,a_time=t_time, a_is_copy_all = k_is_copy_all)
            if t_fail_str != "":
                t_tw.sys().set_return_data()
                a_signal.emit("error",u'拷贝失败:\n' + t_fail_str, True)
                a_event.wait()
            else:
                a_signal.emit("info",u"完成", True)
                time.sleep(0.01)
                a_event.wait()
            a_signal.emit("close","",True)
            a_event.wait()
        elif str( k_sou_type ) == "select" and str( k_des_type ) == "folder_sign":
            t_sou_list = t_tw.sys().get_sys_file()
            try:
                t_des_path = t_tw.task_module(t_database, t_module, t_id_list).get_filebox_with_sign(k_des)["path"]
            except :
                a_signal.emit("error",u'取文件框数据失败'+unicode(k_des), True)
                a_event.wait()                   
            
            t_fail_str = ''
            t_fail_str = com_copy(t_sou_list, t_des_path,a_is_cover = is_cover, a_add_str = k_add_str, a_replace_str = k_replace_str, a_work_log_signal = a_signal, a_fail_str = t_fail_str, a_is_folder_son = True, a_time=t_time, a_is_copy_all = k_is_copy_all)
            if t_fail_str != "":
                t_tw.sys().set_return_data()
                a_signal.emit("error",u'拷贝失败:\n' + t_fail_str, True)
                a_event.wait()                      
            else:
                a_signal.emit("info",u"完成", True)
                time.sleep(0.01)
                a_event.wait()
            a_signal.emit("close","",True)
            a_event.wait()
        else:
            t_tw.sys().set_return_data()
            a_signal.emit("error",u"插件参数配置错误",True)
            a_event.wait()            
    except Exception,e:
        traceback.print_exc()
        
        t_tw.sys().set_return_data()
        a_signal.emit("error",u"插件执行失败",True)
        a_event.wait()    
def copy_sou_path_to_des_path(a_data, a_queue, a_signal, a_event):
    """
    文件筐插件,拷贝提交检查文件 to 目标路径:
    1:  sou_type,        sou类型(文件筐文件/目录标识路径/提交文件字段)    ex: select/sign/check
    2:  des_type,        des类型(手动选择/目录标识)                      ex: select/sign/folder_sign
    3:  sou,             sou标识                        目录文件标识   
    4:  des,             des标识                        目录文件标识   
    5:  add_str,         改名追加字符                   ex:  *_finish|finish_*  这种是 文件名后添加 _finish,并且, 文件名前追加finish_
    6:  replace_str,     改名替换字符                   ex: work,ok|v1,     这种是 文件名中的 work字符替换为ok, 并且,文件名中的 v1去掉
    7:  is_show_log,     显示工作日志                   ex: Y/N
    8:  is_cover         是否覆盖                       ex:Y  将会覆盖
    """
    t_tw              = a_data[0]
    t_database        = a_data[1]
    t_id_list         = a_data[2]
    
    t_module          = t_tw.sys().get_sys_module()
    k_sou_type        = t_tw.sys().get_argv_key( "sou_type" )
    k_des_type        = t_tw.sys().get_argv_key( "des_type" )
    k_sou             = t_tw.sys().get_argv_key( "sou" )
    k_des             = t_tw.sys().get_argv_key( "des" )    
    k_add_str         = t_tw.sys().get_argv_key( "add_str" )
    k_replace_str     = t_tw.sys().get_argv_key( "replace_str" )  
    k_is_cover        = t_tw.sys().get_argv_key( "is_cover" )  
    k_is_copy_all     = t_tw.sys().get_argv_key( "is_copy_all" )
    
    t_dict={"tw":t_tw, "db":t_database, "id_list":t_id_list, "module":t_module,  "sou_type":k_sou_type, "des_type": k_des_type, "sou":k_sou, "des":k_des, \
            "add_str":k_add_str, "replace_str":k_replace_str, "is_cover":k_is_cover, "is_copy_all":k_is_copy_all
            }
    __com_copy_sou_path_to_des_path(t_dict, a_queue, a_signal, a_event )
    

def copy_select_to_select(a_data, a_queue, a_signal, a_event):
    
    """
    文件框菜单插件
    操作：文件框右键选择文件  -----copy---->> 所选文件路径下:
    1:  add_str,         改名追加字符                   ex:  *_finish|finish_*  这种是 文件名后添加 _finish,并且, 文件名前追加finish_
    2:  replace_str,     改名替换字符                   ex: work,ok|v1,     这种是 文件名中的 work字符替换为ok, 并且,文件名中的 v1去掉
    3:  is_show_log,     显示工作日志                   ex: Y/N
    4:  is_cover         是否覆盖                       ex:Y  将会覆盖
    5： is_copy_all      是否拷贝全部文件                为空或填'Y'则拷贝全部文件，否则拷贝最大版本
    """
    
    t_tw              = a_data[0]
    t_database        = a_data[1]
    t_id_list         = a_data[2]

    t_module          = t_tw.sys().get_sys_module()
    k_sou_type        = 'select'
    k_des_type        = 'select'
    k_sou             = ""
    k_des             = ""    
    k_add_str         = t_tw.sys().get_argv_key( "add_str" )
    k_replace_str     = t_tw.sys().get_argv_key( "replace_str" )  
    k_is_cover        = t_tw.sys().get_argv_key( "is_cover" )  
    k_is_copy_all     = t_tw.sys().get_argv_key( "is_copy_all" )
    
    t_dict = {"tw":t_tw, "db":t_database, "id_list":t_id_list, "module":t_module,  "sou_type":k_sou_type, "des_type": k_des_type, "sou":k_sou, "des":k_des, \
            "add_str":k_add_str, "replace_str":k_replace_str, "is_cover":k_is_cover, "is_copy_all":k_is_copy_all
            }
    __com_copy_sou_path_to_des_path(t_dict, a_queue, a_signal, a_event )


def copy_select_to_folder_sign(a_data, a_queue, a_signal, a_event): 
    """
    文件框菜单插件
    操作：文件框选择文件 -----copy---->> 目录标识:
    1:  des,             des标识                        目录文件标识   
    2:  add_str,         改名追加字符                   ex:  *_finish|finish_*  这种是 文件名后添加 _finish,并且, 文件名前追加finish_
    3:  replace_str,     改名替换字符                   ex: work,ok|v1,     这种是 文件名中的 work字符替换为ok, 并且,文件名中的 v1去掉
    4:  is_show_log,     显示工作日志                   ex: Y/N
    5:  is_cover         是否覆盖                       ex:Y  将会覆盖
    6:  is_copy_all      是否拷贝全部文件                为空或填'Y'则拷贝全部文件，否则拷贝最大版本
    """
    t_tw              = a_data[0]
    t_database        = a_data[1]
    t_id_list         = a_data[2]
    
    t_module          = t_tw.sys().get_sys_module()
    k_sou_type        = 'select'
    k_des_type        = 'sign'
    k_sou             = ''
    k_des             = t_tw.sys().get_argv_key( "des" )    
    k_add_str         = t_tw.sys().get_argv_key( "add_str" )
    k_replace_str     = t_tw.sys().get_argv_key( "replace_str" )  
    k_is_cover        = t_tw.sys().get_argv_key( "is_cover" )  
    k_is_copy_all     = t_tw.sys().get_argv_key( "is_copy_all" )
    
    t_dict={"tw":t_tw, "db":t_database, "id_list":t_id_list, "module":t_module,  "sou_type":k_sou_type, "des_type": k_des_type, "sou":k_sou, "des":k_des, \
            "add_str":k_add_str, "replace_str":k_replace_str, "is_cover":k_is_cover, "is_copy_all":k_is_copy_all
            }
    __com_copy_sou_path_to_des_path(t_dict, a_queue, a_signal, a_event )
def copy_folder_sign_to_select(a_data, a_queue, a_signal, a_event):
    """
    右键菜单插件
    操作：目录标识 -----copy---->> 所选目录:
    1:  sou,             sou标识                        目录文件标识   
    2:  add_str,         改名追加字符                   ex:  *_finish|finish_*  这种是 文件名后添加 _finish,并且, 文件名前追加finish_
    3:  replace_str,     改名替换字符                   ex: work,ok|v1,     这种是 文件名中的 work字符替换为ok, 并且,文件名中的 v1去掉
    4:  is_show_log,     显示工作日志                   ex: Y/N
    5:  is_cover         是否覆盖                       ex:Y  将会覆盖
    6:  is_copy_all      是否拷贝全部文件                为空或填'Y'则拷贝全部文件，否则拷贝最大版本
    """
    t_tw              = a_data[0]
    t_database        = a_data[1]
    t_id_list         = a_data[2]
    
    t_module          = t_tw.sys().get_sys_module()
    k_sou_type        = 'sign'
    k_des_type        = 'select'
    k_des             = ""  
    k_sou             = t_tw.sys().get_argv_key( "sou" )   
    k_add_str         = t_tw.sys().get_argv_key( "add_str" )
    k_replace_str     = t_tw.sys().get_argv_key( "replace_str" )  
    k_is_cover        = t_tw.sys().get_argv_key( "is_cover" )  
    k_is_copy_all     = t_tw.sys().get_argv_key( "is_copy_all" )
    
    t_dict={"tw":t_tw, "db":t_database, "id_list":t_id_list, "module":t_module,  "sou_type":k_sou_type, "des_type": k_des_type, "sou":k_sou, "des":k_des, \
            "add_str":k_add_str, "replace_str":k_replace_str, "is_cover":k_is_cover, "is_copy_all":k_is_copy_all
            }
    __com_copy_sou_path_to_des_path(t_dict, a_queue, a_signal, a_event )
def copy_folder_sign_to_folder_sign(a_data, a_queue, a_signal, a_event): 
    """
    右键菜单插件
    操作：目录标识 -----copy---->> 目录标识:
    1:  sou,             sou标识                        目录文件标识   
    2:  des,             des标识                        目录文件标识  
    4:  add_str,         改名追加字符                   ex:  *_finish|finish_*  这种是 文件名后添加 _finish,并且, 文件名前追加finish_
    5:  replace_str,     改名替换字符                   ex: work,ok|v1,     这种是 文件名中的 work字符替换为ok, 并且,文件名中的 v1去掉
    6:  is_show_log,     显示工作日志                   ex: Y/N
    7:  is_cover         是否覆盖                       ex:Y  将会覆盖
    8:  is_copy_all      是否拷贝全部文件                为空或填'Y'则拷贝全部文件，否则拷贝最大版本
    """
    t_tw              = a_data[0]
    t_database        = a_data[1]
    t_id_list         = a_data[2]
    
    t_module          = t_tw.sys().get_sys_module()
    k_sou_type        = 'sign'
    k_des_type        = 'sign'
    k_sou             = t_tw.sys().get_argv_key( "sou" )
    k_des             = t_tw.sys().get_argv_key( "des" )    
    k_add_str         = t_tw.sys().get_argv_key( "add_str" )
    k_replace_str     = t_tw.sys().get_argv_key( "replace_str" )  
    k_is_cover        = t_tw.sys().get_argv_key( "is_cover" )  
    k_is_copy_all     = t_tw.sys().get_argv_key( "is_copy_all" )
    t_dict={"tw":t_tw, "db":t_database, "id_list":t_id_list, "module":t_module,  "sou_type":k_sou_type, "des_type": k_des_type, "sou":k_sou, "des":k_des, \
            "add_str":k_add_str, "replace_str":k_replace_str, "is_cover":k_is_cover, "is_copy_all":k_is_copy_all
            }
    __com_copy_sou_path_to_des_path(t_dict, a_queue, a_signal, a_event )
def copy_check_to_select(a_data, a_queue, a_signal, a_event): 
    """
    流程插件,右键菜单插件
    操作：task.submit_file_path -----copy---->> 所选目录:
    1:  add_str,         改名追加字符                   ex:  *_finish|finish_*  这种是 文件名后添加 _finish,并且, 文件名前追加finish_
    2:  replace_str,     改名替换字符                   ex: work,ok|v1,     这种是 文件名中的 work字符替换为ok, 并且,文件名中的 v1去掉
    3:  is_show_log,     显示工作日志                   ex: Y/N
    4:  is_cover         是否覆盖                       ex:Y  将会覆盖
    5:  is_copy_all      是否拷贝全部文件                为空或填'Y'则拷贝全部文件，否则拷贝最大版本
    """
    t_tw              = a_data[0]
    t_database        = a_data[1]
    t_id_list         = a_data[2]
    
    t_module          = t_tw.sys().get_sys_module()
    k_sou_type        = "check"
    k_des_type        = "select"
    k_sou             = ""
    k_des             = ""   
    k_add_str         = t_tw.sys().get_argv_key( "add_str" )
    k_replace_str     = t_tw.sys().get_argv_key( "replace_str" )  
    k_is_cover        = t_tw.sys().get_argv_key( "is_cover" )  
    k_is_copy_all     = t_tw.sys().get_argv_key( "is_copy_all" )
    
    t_dict={"tw":t_tw, "db":t_database, "id_list":t_id_list, "module":t_module,  "sou_type":k_sou_type, "des_type": k_des_type, "sou":k_sou, "des":k_des, \
            "add_str":k_add_str, "replace_str":k_replace_str, "is_cover":k_is_cover, "is_copy_all":k_is_copy_all
            }
    __com_copy_sou_path_to_des_path(t_dict, a_queue, a_signal, a_event )
def copy_check_to_folder_sign(a_data, a_queue, a_signal, a_event):
    """
    操作：流程插件,右键菜单插件
    task.submit_file_path -----copy---->> 目录标识:
    1:  des,             des标识                        目录文件标识   
    2:  add_str,         改名追加字符                   ex:  *_finish|finish_*  这种是 文件名后添加 _finish,并且, 文件名前追加finish_
    3:  replace_str,     改名替换字符                   ex: work,ok|v1,     这种是 文件名中的 work字符替换为ok, 并且,文件名中的 v1去掉
    4:  is_show_log,     显示工作日志                   ex: Y/N
    5:  is_cover         是否覆盖                       ex:Y  将会覆盖
    6:  is_copy_all      是否拷贝全部文件                为空或填'Y'则拷贝全部文件，否则拷贝最大版本
    """
    t_tw              = a_data[0]
    t_database        = a_data[1]
    t_id_list         = a_data[2]
    
    t_module          = t_tw.sys().get_sys_module()
    k_sou_type        = "check"
    k_des_type        = "sign"
    k_sou             = ""
    k_des             = t_tw.sys().get_argv_key( "des" )    
    k_add_str         = t_tw.sys().get_argv_key( "add_str" )
    k_replace_str     = t_tw.sys().get_argv_key( "replace_str" )  
    k_is_cover        = t_tw.sys().get_argv_key( "is_cover" )  
    k_is_copy_all     = t_tw.sys().get_argv_key( "is_copy_all" )
    
    t_dict={"tw":t_tw, "db":t_database, "id_list":t_id_list, "module":t_module,  "sou_type":k_sou_type, "des_type": k_des_type, "sou":k_sou, "des":k_des, \
            "add_str":k_add_str, "replace_str":k_replace_str, "is_cover":k_is_cover, "is_copy_all":k_is_copy_all
            }
    __com_copy_sou_path_to_des_path(t_dict, a_queue, a_signal, a_event )
def copy_select_to_filebox_sign(a_data, a_queue, a_signal, a_event):
    """
    操作：文件框菜单插件
    文件框所选文件 -----copy---->> 文件框标识:  
    1:  des,             des标识                        文件框标识   
    2:  add_str,         改名追加字符                   ex:  *_finish|finish_*  这种是 文件名后添加 _finish,并且, 文件名前追加finish_
    3:  replace_str,     改名替换字符                   ex: work,ok|v1,     这种是 文件名中的 work字符替换为ok, 并且,文件名中的 v1去掉
    4:  is_show_log,     显示工作日志                   ex: Y/N
    5:  is_cover         是否覆盖                       ex:Y  将会覆盖
    6:  is_copy_all      是否拷贝全部文件                为空或填'Y'则拷贝全部文件，否则拷贝最大版本
    """
    t_tw              = a_data[0]
    t_database        = a_data[1]
    t_id_list         = a_data[2]
    
    t_module          = t_tw.sys().get_sys_module()
    k_sou_type        = "select"
    k_des_type        = "folder_sign"
    k_sou             = ""
    k_des             = t_tw.sys().get_argv_key( "des" )    
    k_add_str         = t_tw.sys().get_argv_key( "add_str" )
    k_replace_str     = t_tw.sys().get_argv_key( "replace_str" )  
    k_is_cover        = t_tw.sys().get_argv_key( "is_cover" )  
    k_is_copy_all     = t_tw.sys().get_argv_key( "is_copy_all" )
    
    t_dict={"tw":t_tw, "db":t_database, "id_list":t_id_list, "module":t_module,  "sou_type":k_sou_type, "des_type": k_des_type, "sou":k_sou, "des":k_des, \
            "add_str":k_add_str, "replace_str":k_replace_str, "is_cover":k_is_cover, "is_copy_all":k_is_copy_all
            }
    __com_copy_sou_path_to_des_path(t_dict, a_queue, a_signal, a_event )
#---------------------------------------------------------------------------骁颖------------------------------------------------------------------------ 


def asset_link_path(a_data, a_queue, a_signal, a_event):
    """
    右键菜单插件,镜头制作 打开/获取 资产link路径:
    1.type:       打开/获取           ex: open/get
    2.folder_sign 资产对应的文件路径   ex: maya_work
    """
    t_tw              = a_data[0]
    t_databse         = a_data[1]
    t_id_list         = a_data[2]
    t_module          = t_tw.sys().get_sys_module()
    t_link_id_list    = t_tw.sys().get_sys_link_id()
    K_folder_sign     = t_tw.sys().get_argv_key("folder_sign")
    K_type            = t_tw.sys().get_argv_key("type")    
    if K_type==False  or str(K_type).strip()=="" or K_folder_sign==False  or str(K_folder_sign).strip()=="":
        a_signal.emit("error",u"参数配置错误!",True)
        a_event.wait()            
    try:
        data_list = t_tw.info_module(t_database,"asset",t_link_id_list).get_field_and_dir(["asset.asset_name","asset.cn_name"], [K_folder_sign])
    except Exception,e:
        data_list = False
    if data_list ==False:
        a_signal.emit("error",u"读取数据库失败!",True)
        a_event.wait()
    try:
        t_data = []
        for data in data_list:
            asset_name  = data['asset.asset_name']
            cn_name     = data['asset.cn_name']
            asset_path  = data[K_folder_sign]
            t_data.append( [asset_name, cn_name, asset_path] )
    except Exception,e:
        a_signal.emit("error",u"数据分析失败!",True)
        a_event.wait()          
    t_exists_list = []
    t_text = u"资产名---------中文名---------路径\n"
    for data in t_data:
        if os.path.exists( unicode(data[2]) ):
            t_exists_list.append( unicode(data[2]) )
            if str(K_type).lower() == "open":
                if ct.com().get_os() == "win":
                    os.startfile( data[2] )
                else:
                    subprocess.call(["open",data[2]])                
                #os.system( 'explorer.exe "%s"' %unicode(data[2]) )
                a_signal.emit("log", u"Info:打开路径%s\n"%unicode(data[2]) , True)
            else:
                t_text = t_text + u"%s--------%s-------%s\n"%(data[0], data[1], data[2])
    if str(K_type).lower() == "get" and t_exists_list!=[]:
        a_signal.emit("log", t_text, True)
        text_path = ct.com().get_tmp_path() + "\\tem_asset_link_path.txt"
        try:
            t_file=open(text_path,"wt")
            t_file.write(t_text.encode('utf-8'))   
            t_file.close()
            #os.system(text_path)
            if ct.com().get_os() == "win":
                os.system(text_path)
            else:
                subprocess.call(["open",text_path])              
        except Exception,e:
            a_signal.emit("error",u"资产路径写入文件失败!",True)
            a_event.wait()            
    if t_exists_list==[]:
        a_signal.emit("error",u"查询的路径不存在!",True)
        a_event.wait()
    a_signal.emit("close","",True)
    a_event.wait()  


def rv_player_mov_filebox(a_data):
    """
    文件筐插件,rv播放视频:(如果默认rv路径不存在,会查询软件路径)
    1:  type,            播放模式           ex: series/tile(串播/并播)
    2:  is_show_log,     是否显示工作日志    ex: Y/N
    """
    t_tw              = a_data[0]
    t_databse         = a_data[1]
    t_id_list         = a_data[2]
    k_type            = t_tw.sys().get_argv_key( "type" )
    t_rv_path         = 'c:/Program Files/rv_player/bin/rv.exe'
    
    if not os.path.exists( t_rv_path ):
        t_rv_path = t_tw.sys().get_argv_key("rv_path")
        if not os.path.exists( t_rv_path ):
            message().error( "rv路径错误!" )
    file_list = t_tw.sys().get_sys_file()
    new_list = []
    for i in file_list:
        if os.path.isdir(i):
            temp_list=ct.file().get_file_with_walk_folder(i)
            new_list=new_list+temp_list
        else:
            new_list.append(i)
    t_new_list=[]
    for i in new_list:
        if i.strip().lower().find("thumbs.db")==-1 and i.strip().lower().find(".ini")==-1:
            t_new_list.append(i)
    
    if len(t_new_list)==0:
        message().error( u"没有找到可以播放文件")
        return 
            
    if str( k_type ).lower().strip() == "tile":
        ct.rv(t_rv_path).tile_play(t_new_list)
    else:
        ct.rv(t_rv_path).series_play(t_new_list)
    sys.exit()
def rv_player_seq_filebox(a_data):
    """
    文件筐插件,rv播放序列图:(如果默认rv路径不存在,会查询软件路径)
    1:  type,            播放模式           ex: series/tile(串播/并播)
    2:  is_show_log,     是否显示工作日志    ex: Y/N
    """
    t_tw              = a_data[0]
    t_databse         = a_data[1]
    t_id_list         = a_data[2]
    k_type            = t_tw.sys().get_argv_key( "type" )
    t_rv_path         = 'c:/Program Files/rv_player/bin/rv.exe'

    if not os.path.exists( t_rv_path ):
        t_rv_path = t_tw.sys().get_argv_key("rv_path")
        if not os.path.exists( t_rv_path ):
            message().error( "rv路径错误!" )            
            
    file_list = t_tw.sys().get_sys_file()
    if len(file_list)==0:
        return
    last_list = []
    new_list  = []
    for i in file_list:
        if os.path.isdir(i):
            try:
                seq_dict = ct.file().get_seq(i, True)
            except Exception, e:
                #里面会有如果路径不存在啥的报错。所以直接跳过
                print e.message
                pass
            else:
                if isinstance(seq_dict, dict) and seq_dict.has_key("path"):
                    last_list.append(seq_dict["path"])
        else:
            last_list.append(i)

    
    if len(last_list)==0:
        message().error( u"没有找到可以播放文件")
        return     
    
    if len(last_list)>0:
        if str( k_type ).lower().strip() == "tile":
            ct.rv(t_rv_path).tile_play(last_list)
        else:
            ct.rv(t_rv_path).series_play(last_list)
    sys.exit()

                
def total_frame(a_data):
    """
    右键菜单插件,统计帧数
    """
    t_tw              = a_data[0]
    t_database        = a_data[1]
    t_id_list         = a_data[2]
    t_module          = t_tw.sys().get_sys_module()
    t_module_type     = t_tw.sys().get_sys_module_type()
    if t_module != "shot":
        message().error(u"只能用于 镜头模块/镜头制作 模块")
    if t_id_list == []:
        message().error(u"至少选择一行!")
    try:    
        if t_module_type == "task":
            shot_id_list = t_tw.task_module(t_database,t_module,t_id_list).get(["shot.id","shot.frame"])
        else:
            shot_id_list = t_tw.info_module(t_database,t_module,t_id_list).get(["shot.id","shot.frame"])
    except:
        message().error(u"取出数据失败!")
    shot_name = {i["shot.id"]:i["shot.frame"] for i in shot_id_list}
    frame_number = 0
    key_list = set(shot_name.keys())
    for shot in key_list:
        if shot_name[shot] == None or shot_name[shot] == "":
            continue
        try:
            t_frame = int(shot_name[shot])
        except Exception, e:
            t_frame = 0
        frame_number += t_frame
    message().info(u"总帧数:\n      %d"%frame_number)
 
            
def seq_to_mov(a_data):
    t_tw              = a_data[0]
    t_databse         = a_data[1]
    t_id_list         = a_data[2]
    """
    序列图转mov
    """
    image_folder_sign  =  t_tw.sys().get_argv_key("image_folder_sign")
    code_format        =  t_tw.sys().get_argv_key("code_format")
    frame_rate         =  t_tw.sys().get_argv_key("frame_rate")
    output_path        =  t_tw.sys().get_argv_key("output_path")
    nuke_path          =  t_tw.sys().get_argv_key("nuke_path")
    #---------------------------------------------------
    is_check="Y"
    try:
        temp=t_tw.sys().get_argv_key("is_check")
        if temp!=False:
            is_check=temp
    except:
        pass

    if image_folder_sign==False or code_format==False or frame_rate==False  or output_path==False  or nuke_path==False  or unicode(image_folder_sign).strip()=="" or unicode(code_format).strip()==""  or unicode(frame_rate).strip()=="":
        message().error(u"取参数失败")
    if os.path.exists(unicode(nuke_path)) ==False:
        message().error( u"nuke路径错误("+nuke_path+")")

    data_list=t_tw.task_module(t_database,"shot",t_id_list).get_field_and_dir(["shot.shot","task.pipeline","shot.frame","task.artist"], [image_folder_sign])    
    if data_list ==False:
        message().error( u"读取数据库数据失败")
    else:
        not_exist=''#不存在的文件集合
        not_match=''#不匹配集合
        try:
            t_nk=ct.nk()
            for data in data_list:
                shot=data['shot.shot']
                pipeline=data['task.pipeline'].lower()
                t_check_frame=data['shot.frame']
                t_artist=data['task.artist']
                image_ok_path=data[image_folder_sign]+"/"
                #==========================================================================11.22====
                if unicode(is_check).strip().lower()=="y":
                    if t_check_frame==0 or t_check_frame=="0" or t_check_frame=="" or t_check_frame==None:
                        if t_check_frame==None:
                            t_check_frame="None"
                        if t_check_frame==0:
                            t_check_frame="0"
                        not_match=not_match+"\n"+t_artist+"----"+shot+"----"+pipeline+"----"+t_check_frame+"----"
                        continue
                    else:
                        res=t_nk.render_mov(nuke_path, image_ok_path, unicode(output_path), code_format, 5, "", t_check_frame,"sRGB", frame_rate)
        
                else:#不检查
                    res=t_nk.render_mov(nuke_path, image_ok_path, unicode(output_path), code_format, 5, "", 0, "sRGB", frame_rate)
                    
                if res==False:#返回失败退出
                    sys.exit()
                elif type(res)==dict:
                    if res['type']=='not_match':#帧数不匹配
                        not_match=unicode(not_match)+"\n"+unicode(t_artist)+"----"+unicode(shot)+"----"+unicode(pipeline)+"----"+unicode(t_check_frame)+"----"+unicode(res["frame_count"])
                    elif res['type']=='not_sequence':#不是连续的序列帧
                        not_exist=not_exist+"\n"+unicode(t_artist)+"----"+shot+"----"+pipeline
                    else:#合成后mov不存在
                        not_exist=not_exist+"\n"+unicode(t_artist)+"----"+shot+"----"+pipeline   
                        
            

        except Exception,e:
            message().error(u"批量合成Mov失败")
        else:

            if not_exist!="" or not_match !="":
                error=""
                if not_match!="":
                    error=error+u"帧数不匹配如下:\n"+u"制作者----shot----pipeline----系统帧数----image_ok帧数"+not_match+"\n\n"
                if  not_exist !="":
                    error=error+u"合成Mov失败 或 非连续序列帧如下:\n"+u"制作者--------shot---------pipeline"+not_exist
                message().error( error)
            else:
                message().info( u"完成"+"\n"+u"mov路径为:"+"( "+output_path+" )")

def __sorted(lis, is_reverse=False):  
    lists=list(lis)
    count=len(lists)
    for i in range(0,count):
        for j in range(i+1,count):
            if is_reverse:
                if unicode(os.path.basename(lists[i])).lower() < unicode( os.path.basename(lists[j])).lower():
                    lists[i],lists[j]=lists[j],lists[i]
            else:
                if unicode( os.path.basename(lists[i])).lower() > unicode( os.path.basename(lists[j])).lower():
                    lists[i],lists[j]=lists[j],lists[i]		
    return lists

def rv_submit_file(a_data):
    t_tw              = a_data[0]
    t_databse         = a_data[1]
    t_id_list         = a_data[2]
    """
    提交文件,rv串播
    """    
    t_dict          = {}
    t_file_list     = []
    t_file_name     = []
    t_new_file_list = []
    t_file_new_list = []
    t_rv_path         = 'c:/Program Files/rv_player/bin/rv.exe'
    if not os.path.exists( t_rv_path ):
        t_rv_path = t_tw.sys().get_argv_key("rv_path")
    if t_rv_path==False or unicode(t_rv_path).strip()=="":
        message().error(u"rv_path参数配置错误")
    t_module=t_tw.sys().get_sys_module()
    t_module_type=t_tw.sys().get_sys_module_type()
    if t_module_type!="task":
        message().error( u"只能用于task模块")
        return None
    try:
        t_class=t_tw.task_module(t_database,t_module,t_id_list)
        data_list=t_class.get(["task.submit_file_path"])
    except:
        data_list = False
    t_path_sign="task.submit_file_path"
    if data_list==False or data_list==[]:
        message().error(u"数据库查询失败")
        return None
    for data in data_list:
        if data[t_path_sign]!=None and data[t_path_sign]!="":
            try:
                t_submit_file_path=json.loads(data[t_path_sign])
                if isinstance(t_submit_file_path, dict) and t_submit_file_path.has_key("file_path"):
                    t_file_path_list=t_submit_file_path["file_path"]
                    if isinstance(t_file_path_list, list):
                        for i in t_file_path_list:
                            t_file_list.append(i)
            except Exception, e:
                message().error( u"读取提交文件失败")
    #————————————————————————————
     
    for i in t_file_list:
        if i.strip().lower().find("thumbs.db")==-1 and os.path.exists(i):
            t_file_new_list.append(unicode(i).replace("\\","\\\\"))
    

    
    if len(t_file_new_list)==0:
        message().error( u"没有找到可以播放文件")
        return 
    try:
        t_file_new_list = __sorted(t_file_new_list)
        ct.rv(t_rv_path).series_play(t_file_new_list)
    except Exception,e :
        message().error(traceback.format_exc())
    sys.exit()
def subimt_file_and_filebox_file_rv(a_data):
    t_tw              = a_data[0]
    t_databse         = a_data[1]
    t_id_list         = a_data[2]
    """
    提交文件,rv并播
    """    
    t_file_list=[]
    t_file_new_list=[]
    t_rv_path         = 'c:/Program Files/rv_player/bin/rv.exe'
    if not os.path.exists( t_rv_path ):
        t_rv_path = t_tw.sys().get_argv_key("rv_path")
    if t_rv_path==False or str(t_rv_path).strip()=="":
        message().error(u"rv_path参数配置错误")
        
    t_module=t_tw.sys().get_sys_module()
    t_module_type=t_tw.sys().get_sys_module_type()
    if t_module_type!="task":
        message.error(u"只能用于task模块")
        return None
    try:
        t_class=t_tw.task_module(t_database,t_module,t_id_list)
        data_list=t_class.get(["task.submit_file_path"])
    except:
        data_list = False
    t_path_sign="task.submit_file_path"
    if data_list==False or data_list==[]:
        message.error(u"数据库查询失败")
        return None
    for data in data_list:
        if data[t_path_sign]!=None:
            t_file_path=json.loads(data[t_path_sign])["file_path"][0]
            t_file_list.append(t_file_path)
    for i in t_file_list:
        if i.strip().lower().find("thumbs.db")==-1 and os.path.exists(i):
            t_file_new_list.append(i)   
    file_list_folder=t_tw.sys().get_sys_file()#文件狂的条目
    if file_list_folder==False or file_list_folder==[]:#取文件框文件有问题
        return
    new_list=[]
    for i in file_list_folder:
        if os.path.isdir(i):
            temp_list=ct.file().get_file_with_walk_folder(i)
            new_list=new_list+temp_list
        else:
            new_list.append(i)
    t_new_list=[]
    for i in new_list:
        if i.strip().lower().find("thumbs.db")==-1:
            t_new_list.append(i)
    tile_list=t_new_list+t_file_new_list
    ct.rv(t_rv_path).tile_play(tile_list)
    sys.exit()
def image_stitching(t_tw, t_database, t_id_list):
    #图片拼接，并生成一个新的图片,不复制原先的图片
    t_folder = t_tw.sys().get_sys_folder()
    is_error=False
    if t_folder==False or str(t_folder)=="":
        t_tw.sys().set_return_data()
        message().error( u"取目录失败" )
    if os.path.exists(t_folder)==False:
        t_tw.sys().set_return_data()
        message().error( u"目录("+t_folder+u")未创建" )    
        
    file_path_list = t_tw.sys().get_sys_file()
    if isinstance(file_path_list,list)==False:
        t_tw.sys().set_return_data()
        message().error( u"提交文件类型错误" )
    if len(file_path_list)<=0:
        t_tw.sys().set_return_data()
        message().error( u"没有找到提交文件" )
        
    try:
        des_file_path=""
        total=""
        t_uuid_file_list=[]
        file_path_list.sort()
        for i in file_path_list:
            if des_file_path=="":
                des_file_path=t_folder+"/"+os.path.basename(i)
            if ct.com().exist_chinese(i):
                temp_file=ct.com().get_tmp_path()+"/"+str(ct.com().uuid())+"."+os.path.splitext(i)[1]
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                #===============骁颖==2018.06.15=====================     
                #shutil.copyfile(i, temp_file)
                ct.file().copy_file(i, temp_file)
                #===============骁颖==2018.06.15===================== 
                t_uuid_file_list.append(temp_file)
                total=total+' '+'"'+temp_file+'"'
            else:
                total=total+' '+'"'+i+'"'
        res=convert_image_stitching(t_tw,total, os.path.splitext(des_file_path)[1])
        if res!=False:
            if os.path.exists(des_file_path):
                os.remove(des_file_path)
            #===============骁颖==2018.06.15===================== 
            #shutil.copyfile(res, des_file_path)
            ct.file().copy_file(res, des_file_path)
            #===============骁颖==2018.06.15===================== 
        for i in t_uuid_file_list:
            os.remove(i)
        t_tw.sys().set_return_data()
    except Exception,e:
        t_tw.sys().set_return_data()
        message().error( u"拼接图片失败" )
def convert_image_stitching(t_tw, total_image, t_format):
    out_put      = ct.com().get_tmp_path()+"/image_stitching"+t_format 
    convert_path = G_cgtw_path + "/convert.exe"
    if os.path.exists(convert_path)==False:
        t_tw.sys().set_return_data()
        message().error(u"( "+convert_path+u" ) 文件不存在")
    cmd='"'+convert_path+'" '+total_image+" -gravity south +append "+'"'+out_put+'"'
    ct.com().exec_cmd(cmd)
    if os.path.exists(out_put)==False or os.path.getsize(out_put) <=0:
        t_tw.sys().set_return_data()
        message().error(u"调用转换命令，拼接失败!!!")
    else:
        return out_put 

def open_with(a_tw):
    """
    指定软件打开:
    1:  software,    软件路径  
    2:  argument,      目标目录标识   key可以不填写
    """    
    t_software=a_tw.sys().get_argv_key("software")
    t_argument=a_tw.sys().get_argv_key("argument")#额外参数
    file_list=a_tw.sys().get_sys_file()
    if file_list==False or len(file_list)==0:#取文件框文件有问题
        message().error(u"请选择文件")

    if t_software==False  or os.path.exists(unicode(t_software))==False:
        message().error(u"参数配置错误")
    try:
        if len(file_list)>0:
            t_file_path=unicode(file_list[0]).replace("\\", "/")
            #删除首尾的引号
            t_software=unicode(t_software).strip()
            if t_software[0]=='"':
                t_software=t_software[1:]
            if t_software[-1]=='"':
                t_software=t_software[:-1]

            if t_argument==False or unicode(t_argument).strip()=="":
                ct.com().exec_cmd('"'+t_software+'" '+'"'+t_file_path+'"')
            else:
                ct.com().exec_cmd('"'+t_software+'" '+t_argument+' "'+t_file_path+'"')
    except:
        message().error(u"打开文件失败:\n"+unicode(traceback.format_exc()))

def convert_seq_format(a_tw, a_db, a_id_list):
    """
    转序列图格式:
    1:  source_folder_sign,    源目录标识   
    2:  destination_folder_sign,      目标目录标识
    3:  source_format,      文件格式,只能单个如png
    4:  destination_format    文件格式,只能单个如png  
    """

    is_fail=""
    source_folder_sign       =t_tw.sys().get_argv_key("source_folder_sign")
    destination_folder_sign  =t_tw.sys().get_argv_key("destination_folder_sign")
    source_format            =t_tw.sys().get_argv_key("source_format")
    destination_format       =t_tw.sys().get_argv_key("destination_format")
    t_module=a_tw.sys().get_sys_module()
    t_module_type=a_tw.sys().get_sys_module_type()
    if t_module_type!="task":
        message.error(u"只能用于task模块")
    
    if source_folder_sign==False or destination_folder_sign==False or source_format==False or destination_format==False or unicode(source_folder_sign).strip()=="" or unicode(destination_folder_sign).strip()=="" or unicode(source_format).strip()=="" or unicode(destination_format).strip()=="":
        message().error(u"插件配置错误")    
    try:
        data_list=a_tw.task_module(a_db,t_module,t_id_list).get_dir([source_folder_sign,destination_folder_sign])
        if data_list==[]:
            message.error(u"没有取到数据")
        
        for data in data_list:
            t_sou_folder=data[source_folder_sign]
            t_des_folder=data[destination_folder_sign]
            if os.path.exists(t_sou_folder):
                for src in os.listdir(t_sou_folder):
                    t_path=t_sou_folder+"/"+src
                    if os.path.isdir(t_path) and unicode(src).lower()!="history":
                        t_sou_file_list=ct.file().get_path_list(t_path,["*."+source_format])
                        for t_sou_file in t_sou_file_list:
                            t_des_file=t_des_folder+"/"+src+"/"+os.path.splitext(os.path.basename(t_sou_file))[0]+"."+destination_format
                            if not os.path.exists(os.path.dirname(t_des_file)):
                                os.makedirs(os.path.dirname(t_des_file))
                            print u"convert "+t_sou_file.replace("\\","/")+" --> "+t_des_file.replace("\\","/")
                            res=ct.mov().image_to_image(t_sou_file.replace("\\","/"), t_des_file.replace("\\","/"))
                            if res==False:
                                is_fail=is_fail+t_sou_file.replace("\\","/")+"---------->"+t_des_file.replace("\\","/")+"\n"
        
    except:
        message().error(u"转序列图根式失败:\n"+unicode(traceback.format_exc()))
    else:
        if is_fail=="":
            message().info(u"完成")
        else:
            message.error(u"转换失败如下:\n"+unicode(is_fail))    

    


def bulk_submit(a_data, a_queue, a_signal, a_event):
    """
    批量提交,但只是改状态:
    1:  is_exist_file_submit, 是否文件存在才会提交      ex: Y/N    key可以不填写      
    """    
    t_tw              = a_data[0]
    t_databse         = a_data[1]
    t_id_list         = a_data[2]

    k_is_exist_file_submit = t_tw.sys().get_argv_key( "is_exist_file_submit" )
    t_module          = t_tw.sys().get_sys_module()    
    t_module_type     = t_tw.sys().get_sys_module_type()
    
    #------模块处理
    if t_module_type!="task":
        a_signal.emit("error", u"仅允许在 (task) 模块使用本插件!", True)
        a_event.wait()
    
    if t_module != "shot" and t_module != "asset":
        a_signal.emit("error", u"只能用于镜头制作或者资产制作", True)
        a_event.wait()        
    
    error=''#不存在的文件集合    
    try:
        sign_list=[]
        if t_module=="shot":
            sign_list=["shot.shot"]
        else:
            sign_list=["asset.asset_name"]
            
        data_list = t_tw.task_module(t_databse, t_module, t_id_list).get( sign_list )
        if data_list==[]:
            a_signal.emit("error", u"没有取到数据", True)
            a_event.wait()     
            
        for data in data_list:
            t_id=data["id"]
            temp=data[ sign_list[0] ]
            a_signal.emit("log",  u'获取提交文件框信息-->  ( '+temp+' )', False)
            t_class_work=t_tw.task_module(t_databse, t_module, [t_id])
            file_data_dict=t_class_work.filebox_get_submit_data()
            if file_data_dict==False or file_data_dict=={}:
                error=error+"\n"+temp
            else:
                a_signal.emit("log",  u'查找最大版本的提交文件-->  ( '+temp+' )', False)
                rule_list=file_data_dict["rule"]
                t_path=file_data_dict["path"]
                new_rule_list=[]
                for i in rule_list:
                    new_rule_list.append(unicode(i).replace("#","[0-9]"))

                t_submit_file=""
                t_temp_file_list=ct.file().get_path_list( t_path, new_rule_list )
                t_temp_file_list.reverse()
                t_path_list=[]
                t_file_path_list=[]
                for i in t_temp_file_list:
                    base_name=os.path.basename(i)
                    if unicode(base_name).lower()!="history":
                        t_path_list.append(unicode(i).replace("\\", "/"))
                        if os.path.isfile(i):
                            t_file_path_list.append(unicode(i).replace("\\", "/"))
                        else:
                            for temp_path in ct.file().get_file_with_walk_folder(i, ['*.*']):
                                if not os.path.splitext(os.path.basename(temp_path))[-1] in [".db",".ini"]:    
                                    t_file_path_list.append(temp_path.replace("\\","/"))                                

                #文件存在才会提交
                if k_is_exist_file_submit !=False and unicode(k_is_exist_file_submit).strip().lower()=="y":
                    if len(t_path_list)==0 :
                        continue
                    
                a_signal.emit("log",  u'提交-->  ( '+temp+' )', False)
                res=t_class_work.submit(t_file_path_list, "", t_path_list)
                if res==False:
                    error=error+"\n"+temp        
        
        
    except Exception,e:
        a_signal.emit("error", u"批量提交失败:\n"+unicode(traceback.format_exc()), True)
        a_event.wait()
    else:
        if error != "":
            a_signal.emit("log",  u'批量提交失败如下:\n' + error, False)
            a_signal.emit("error", u'批量提交失败如下:\n' + error, True)
            a_event.wait()
        else:
            a_signal.emit("info",u"完成", True)
            a_event.wait()          
    



if __name__ == "__main__":
    try:
        t_tw       = tw()
        t_database = t_tw.sys().get_sys_database()
        t_id_list  = t_tw.sys().get_sys_id()
        t_action   = t_tw.sys().get_argv_key("action")
        t_show_log = t_tw.sys().get_argv_key("is_show_log")
        if str( t_show_log ).lower() == "y":
            t_show_log = True
        else:
            t_show_log = False
    except:
        message().error(u"插件执行失败!")
        
    if   t_action=="drag_image_get_thumbnail":
        show_log(drag_image_get_thumbnail,        [t_tw, t_database, t_id_list], t_show_log)
    elif t_action=="drag_mov_get_thumbnail":
        show_log(drag_mov_get_thumbnail,          [t_tw, t_database, t_id_list], t_show_log)
    elif t_action=="rv_player_mov_filebox":
        rv_player_mov_filebox([t_tw, t_database, t_id_list])
    elif t_action=="rv_player_seq_filebox":
        rv_player_seq_filebox([t_tw, t_database, t_id_list])
    elif t_action=="copy_sou_path_to_des_path":
        show_log(copy_sou_path_to_des_path,       [t_tw, t_database, t_id_list], t_show_log)
    elif t_action=="total_frame":
        total_frame([t_tw, t_database, t_id_list])
    elif t_action=="asset_link_path":    
        show_log(asset_link_path,                 [t_tw, t_database, t_id_list], t_show_log)  
    elif t_action=="seq_to_mov":
        seq_to_mov([t_tw, t_database, t_id_list])  
    elif t_action=="rv_submit_file":  
        rv_submit_file([t_tw, t_database, t_id_list])  
    elif t_action=="subimt_file_and_filebox_file_rv":
        subimt_file_and_filebox_file_rv([t_tw, t_database, t_id_list])  
    elif t_action=="image_stitching":
        image_stitching(t_tw, t_database, t_id_list)
    elif t_action=="open_with":
        open_with(t_tw)
    elif t_action=="convert_seq_format":
        convert_seq_format(t_tw, t_database, t_id_list)
    elif t_action=="bulk_submit":
        show_log(bulk_submit,  [t_tw, t_database, t_id_list], t_show_log)    
    
#---------------------------------------------------------------------------骁颖------------------------------------------------------------------------ 
    elif t_action == 'copy_select_to_select':
        show_log(copy_select_to_select,   [t_tw, t_database, t_id_list], t_show_log)
    elif t_action == 'copy_select_to_folder_sign':
        show_log(copy_select_to_folder_sign,   [t_tw, t_database, t_id_list], t_show_log)
    elif t_action == 'copy_folder_sign_to_select':
        show_log(copy_folder_sign_to_select,   [t_tw, t_database, t_id_list], t_show_log)
    elif t_action == 'copy_folder_sign_to_folder_sign':
        show_log(copy_folder_sign_to_folder_sign,   [t_tw, t_database, t_id_list], t_show_log)
    elif t_action == 'copy_check_to_select':
        show_log(copy_check_to_select,   [t_tw, t_database, t_id_list], t_show_log)
    elif t_action == 'copy_check_to_folder_sign':
        show_log(copy_check_to_folder_sign,   [t_tw, t_database, t_id_list], t_show_log)
    elif t_action == 'copy_select_to_filebox_sign':
        show_log(copy_select_to_filebox_sign,   [t_tw, t_database, t_id_list], t_show_log)      
#---------------------------------------------------------------------------骁颖------------------------------------------------------------------------ 

    
    else:
        message().error(u"未查询到action对应插件!")