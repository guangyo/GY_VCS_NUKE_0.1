# -*- coding: utf-8 -*-
#Author  :王晨飞
#Time    :2017-12-29
#Describe:nuke模板
#         CgTeamWork_V5整理
import os
import sys
import json
import subprocess 
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
from   cgtw            import *
def create_nuke_template(a_data, a_queue, a_signal,a_event):
    t_tw            = a_data[0]
    t_database      = a_data[1]
    t_id_list       = a_data[2]
    t_module        = t_tw.sys().get_sys_module()
    #------------取参数
    try:
        k_nuke_path       = t_tw.sys().get_argv_key("nuke_path")          #nuke路径
        k_template_path   = t_tw.sys().get_argv_key("template_path")          #模板文件路径
        file_input_path   = t_tw.sys().get_argv_key("file_input_path_sign")   #文件输出路径目录标识
        write_input_path  = t_tw.sys().get_argv_key("write_input_path_sign")  #write节点输出路径目录标识
        file_name_rule    = t_tw.sys().get_argv_key("file_name_rule")         #输出文件命名规则
        data_list = t_tw.task_module(t_database, t_module, t_id_list).get_field_and_dir( ["shot.source","shot.shot","eps.eps_name","task.pipeline"] , [file_input_path, write_input_path])
    except Exception,e:
        data_list = []
    if data_list==False or data_list==[]:
        a_signal.emit("error",u"读取数据库失败",True)
        a_event.wait()
    t_fail_list = []
    for data in data_list:
        t_shot             = data["shot.shot"]
        t_eps              = data["eps.eps_name"]
        t_pipeline         = data["task.pipeline"]
        t_source           = data["shot.source"]
        t_file_input_path  = data[file_input_path]
        t_write_input_path = data[write_input_path]
        t_file_name        = file_name_rule.replace("{shot}",t_shot).replace("{eps}",t_eps).replace("{pipeline}",t_pipeline)
        t_des_file         = unicode(t_file_input_path + "/" + t_file_name).replace("\\","/")
        a_signal.emit("log",u"Info:生成文件中(%s-%s-%s)--->%s"%(t_eps,t_shot,t_pipeline,t_file_name), True)
        try:
            t_avi_info  = ct.mov().get_avi_info( t_source )
        except Exception,e:
            t_avi_info  = False
        if t_avi_info==False:
            a_signal.emit("log",u"Error:生成文件失败(%s-%s-%s)--->%s"%(t_eps,t_shot,t_pipeline,t_file_name), True)
            t_fail_list.append( "%s---%s---%s"%(t_eps,t_shot,t_pipeline))
        else:
            try:
                if not os.path.exists(t_file_input_path):
                    os.makedirs( t_file_input_path )
                subprocess.Popen( [k_nuke_path, "-t" , G_base_path+"/nuke_plugin/nuke_template.py", k_template_path, t_des_file, t_write_input_path, t_source, json.dumps(t_avi_info)] ).wait()
            except Exception,e:
                a_signal.emit("log",u"Error:生成文件失败(%s-%s-%s)--->%s"%(t_eps,t_shot,t_pipeline,t_file_name), True)
                t_fail_list.append( "%s---%s---%s"%(t_eps,t_shot,t_pipeline))                
            if os.path.exists( t_des_file ):
                a_signal.emit("log",u"Success:生成文件成功(%s-%s-%s)--->%s"%(t_eps,t_shot,t_pipeline,t_file_name), True)
            else:
                a_signal.emit("log",u"Error:生成文件失败(%s-%s-%s)--->%s"%(t_eps,t_shot,t_pipeline,t_file_name), True)
                t_fail_list.append( "%s---%s---%s"%(t_eps,t_shot,t_pipeline))
    if t_fail_list!=[]:
        t_fail_list = list(set(t_fail_list))
        a_signal.emit("error",u"以下文件生成失败:\n" + "\n".join(t_fail_list), True)
        a_event.wait()
    else:
        a_signal.emit("info",u"完成", True)
        a_event.wait()
if __name__ == "__main__":
    try:
        t_tw       = tw()
        t_database = t_tw.sys().get_sys_database()
        t_id_list  = t_tw.sys().get_sys_id()
        t_show_log = t_tw.sys().get_argv_key("is_show_log")
        if str(t_show_log).lower()=="y":
            t_show_log = True
        else:
            t_show_log = False
    except Exception,e:
        message().error(u"连接CgTeamwork失败!")
    show_log(create_nuke_template, [t_tw, t_database, t_id_list], t_show_log)
    
    