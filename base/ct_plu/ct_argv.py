# -*- coding: utf-8 -*-
import os
import sys
import json

base_path = os.path.dirname( os.path.dirname( __file__.replace("\\","/") ) )
if not base_path in sys.path:
    sys.path.append( base_path )
from  cgtw import *

class ct_argv():
    __sys_dict_data={}
    __argv_dict_data={}
    __filebox_dict_data={}
    def __init__(self, a_dict_data={}):
        #a_dict_data={"sys_data":{"database":"xx"}, "filebox_data":"xx"},格式
        if isinstance(a_dict_data, dict) and a_dict_data.has_key("sys_data") and a_dict_data.has_key("filebox_data"):
            if isinstance(a_dict_data["sys_data"], dict):
                self.__sys_dict_data=a_dict_data["sys_data"]
            if isinstance(a_dict_data["filebox_data"], dict):#文件框配置的数据
                self.__filebox_dict_data=a_dict_data["filebox_data"]
                if self.__filebox_dict_data.has_key("plugin_id") and self.__filebox_dict_data.has_key("type"): 
                    t_plugin_id=self.__filebox_dict_data["plugin_id"]#文件框拖入列表中的字典下的ID为插件的ID
                    t_type=self.__filebox_dict_data["type"]
                    #取插件参数(只有user插件才会取)
                    if t_type=="drag_before_plugin" or t_type=="drag_after_plugin":
                        self.__argv_dict_data=self.__get_plugin_argv(t_plugin_id)
                    
                    #如果文件框有配置参数,插件管理的参数和文件的参数叠加
                    if self.__filebox_dict_data.has_key("argv"):
                        try:                            
                            t_filebox_argv_dict_data=self.__com_get_argv(self.__filebox_dict_data["argv"])
                        except Exception,e:
                            raise Exception(e.message)
                        self.__argv_dict_data=dict(self.__argv_dict_data.items()+t_filebox_argv_dict_data.items())    
    
    #取文件框设置当前项的值
    def get_filebox_data(self):
        return self.__filebox_dict_data

    #取调试用的数据
    def get_debug_argv_dict(self):
        t_dict={}
        try:
            t_res=tw().local_con._send("main_widget", "get_drag_in_plugin_debug_data", {}, "get")
        except Exception, e:
            return t_dict
        else:
            t_dict=t_res
        return t_dict
        
                
    
    #取文件框参数的key
    def get_filebox_key(self, a_key):
        t_argv_data=self.__filebox_dict_data
        if isinstance(t_argv_data, dict):
            if t_argv_data.has_key(a_key):
                return t_argv_data[a_key]
        return False	        
    
    def __com_get_argv(self, a_argv):
        if a_argv=="" or a_argv==[] or a_argv=={}:
            return {}
        
        t_argv_dict={}
        try:
            t_argv=a_argv
            if not isinstance(t_argv, dict):
                try:
                    t_argv=json.loads(t_argv)
                except Exception,e:
                    return {}
                    
            if isinstance(t_argv, dict):
                t_key_list=t_argv.keys()
                for t_key in t_key_list:                 
                    if isinstance(t_argv[t_key], dict) and t_argv[t_key].has_key("value"):
                        t_argv_dict[t_key]=t_argv[t_key]["value"]
                        
        except Exception,e:
            raise Exception(e.message)
        return t_argv_dict
    
    #取插件参数
    def __get_plugin_argv(self, a_plugin_id):
        t_plugin_argv={}
        try:
            t_tw = tw()
            t_argv=t_tw.con()._send("c_plugin","get_one_with_id", {"id":a_plugin_id, "field":"argv"})
            t_plugin_argv=self.__com_get_argv(t_argv)
                        
        except Exception,e:
            raise Exception(e.message)
        
        return t_plugin_argv
            
        
    def get_argv_key(self, a_key):
        t_argv_data=self.__argv_dict_data
        if isinstance(t_argv_data, dict):
            if t_argv_data.has_key(a_key):
                return t_argv_data[a_key]
        return False	



    #------------------------------取系统的数据------------------------------------
    def __get_sys_key(self, a_key):
        t_argv_data=self.__sys_dict_data
        if type(t_argv_data)==type({}) and t_argv_data.has_key(a_key):
            return t_argv_data[a_key]					
        return False
    
    #取版本ID
    def get_version_id(self):
        return self.__get_sys_key('version_id')    
    #取数据库
    def get_sys_database(self):
        return self.__get_sys_key('database')

    #取界面选择ID列表
    def get_sys_id(self):
        return self.__get_sys_key('id_list')
    #取当前模块
    def get_sys_module(self):
        return self.__get_sys_key('module')	
    #当前模块类型
    def get_sys_module_type(self):
        return self.__get_sys_key("module_type")
    #取拖入的源文件列表
    def get_sys_file(self):
        return self.__get_sys_key('file_path_list')
    #取拖入后的目标文件列表
    def get_sys_des_file(self):                              #获取拖入目标完整路径
        return self.__get_sys_key("des_file_path_list")
    #文件框所在的目录路径
    def get_sys_folder(self):
        return self.__get_sys_key('folder')
    #取文件框ID
    def get_sys_filebox_id(self):
        return self.__get_sys_key('filebox_id')
if __name__ == "__main__":
    t_dict_data={"sys_data":{"database":"proj_big", "module":"shot", "module_type":"info"},
                "filebox_data":{"id":"D4A7602E-0406-69BC-376B-839C5D6F0785", "type":"drag_before_plugin", "argv":{"action":{"description":u"描述", "value":"copy_file"}}}}
    t_argv=ct_argv(t_dict_data)
    #print t_argv.get_sys_database()
    #print t_argv.get_sys_file()
    #print t_argv.get_sys_module()
    #print t_argv.get_argv_key("action")
    #print t_argv.get_filebox_key("type")

    

    