#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<deming>
  Purpose: Filebox open nuke file
  Created: 2018/02/20
"""
import os
import sys
import subprocess
t_plugin_path=os.path.dirname(__file__.replace("\\", "/")) 
t_base_path=os.path.dirname(t_plugin_path)
if t_base_path not in sys.path:
    sys.path.append(t_base_path)
    sys.path.append(t_base_path+"/com_lib")
import cgtw
from com_message_box import  message
import re
def run():
    t_tw=cgtw.tw()
    try:
        t_database=t_tw.sys().get_sys_database()
        t_module=t_tw.sys().get_sys_module()
        t_id_list=t_tw.sys().get_sys_id()
        if len(t_id_list)==0 or isinstance(t_id_list, list)==False:
            message().error(u"请选项任务")
        t_nuke_data=t_tw.con._send("c_software", "get_path_and_argv_with_type", {"db":t_database, "type":"nuke"}) 
        if t_nuke_data.has_key('path')==False and t_nuke_data.has_key("argv")==False:
            message().error(u"读取软件路径失败, 请检查是否有配置nuke类型的软件, 注意:类型是小写的nuke")
        t_nuke_path=t_nuke_data["path"].strip()
        t_argv=re.sub("\s+", " ", t_nuke_data["argv"].strip())
        t_argv=t_argv.replace("./base", t_base_path)

        if not os.path.exists(t_nuke_path):
            message().error(u"请确认Nuke安装路径是否存在")
        t_filebox_id=t_tw.sys()._get_sys_key("filebox_id")
        t_file_list=t_tw.sys().get_sys_file()
        t_file=""
        if len(t_file_list)!=0:
            t_file=t_file_list[0]
        t_os=t_tw.sys().get_sys_os()
        t_cmd=' '.join([t_nuke_path, t_argv, t_database, t_module, "id:"+t_id_list[0], t_filebox_id, t_file])
        subprocess.call(t_cmd)
       
    except Exception, e:
        print e
        message().error(e.message)
if __name__=="__main__":
    run()