#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<deming>
  Purpose: Filebox open maya file
  Created: 2018/02/20
"""
import os
import sys
import logging

for k, v in logging.Logger.manager.loggerDict.iteritems():
    if isinstance(v, logging.Logger) and ("requests" in k or "pyside" in k or "pyside2" in k):
        v.setLevel(logging.CRITICAL)
t_plugin_path=os.path.dirname(__file__) 
t_base_path=os.path.dirname(t_plugin_path)
if t_base_path not in sys.path:
    sys.path.append(t_base_path)
    sys.path.append(t_base_path+"/com_lib")
import cgtw
from com_message_box import  message
import re, subprocess
def run():
    try:
        t_tw=cgtw.tw()
        t_database=t_tw.sys().get_sys_database()
        t_module=t_tw.sys().get_sys_module()
        t_id_list=t_tw.sys().get_sys_id()
        if len(t_id_list)==0 or isinstance(t_id_list, list)==False:
            message().error(u"请选项任务")
            
            
        t_maya_data=t_tw.con._send("c_software", "get_path_and_argv_with_type", {"db":t_database, "type":"maya"}) 
        if t_maya_data.has_key('path')==False and t_maya_data.has_key("argv")==False:
            message().error(u"读取软件路径失败, 请检查是否有配置nuke类型的软件, 注意:类型是小写的nuke")
        t_maya_path=t_maya_data["path"].strip()
        t_argv=re.sub("\s+", " ", t_maya_data["argv"].strip())
        t_argv=t_argv.replace("./base", t_base_path)
    
        if not os.path.exists(t_maya_path):
            message().error(u"请确认maya安装路径是否存在")
        t_filebox_id=t_tw.sys()._get_sys_key("filebox_id")
        t_file_list=t_tw.sys().get_sys_file()
        t_file=""
        if len(t_file_list)!=0:
            t_file=t_file_list[0]
        t_cmd=' '.join([t_maya_path, t_argv, t_database, t_module, "id:"+t_id_list[0], t_filebox_id, "False", "file:"+t_file])
        subprocess.call(t_cmd)        
    except Exception, e:
        message().error(e.message)
if __name__=='__main__':
    run()