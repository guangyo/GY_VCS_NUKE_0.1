# coding: utf-8
import os,sys
from _con_local import _con_local

class _client:
    
    @staticmethod
    def _get_uuid():
	if len(sys.argv) < 2 :
	    return ""
	else:
	    return sys.argv[-1]
	
    @staticmethod
    def __get_argv_data():
	t_dic={"plugin_uuid":_client._get_uuid()}
	return _con_local.send_socket("main_widget", "get_plugin_data", t_dic, "get")		

    @staticmethod
    def get_argv_key(T_key, T_argv_data={}):
	if T_argv_data=={}:
	    T_argv_data=_client.__get_argv_data()
	if type(T_argv_data)==type({}) and T_argv_data.has_key('argv'):
	    if type(T_argv_data['argv'])==type({}) and T_argv_data['argv'].has_key(T_key):
		return T_argv_data['argv'][T_key]
	return False	

    @staticmethod
    def get_sys_key(T_key):
	T_argv_data=_client.__get_argv_data()
	if type(T_argv_data)==type({}) and T_argv_data.has_key(T_key):
	    return T_argv_data[T_key]					
	return False	
    
    @staticmethod
    def get_database():
	return _client.get_sys_key('database')

    @staticmethod
    def get_id():
	return _client.get_sys_key('id_list')

    @staticmethod
    def get_link_id():
	return _client.get_sys_key('link_id_list')

    @staticmethod
    def get_module():
	return _client.get_sys_key('module')	
    
    @staticmethod
    def get_module_type():
	return _client.get_sys_key("module_type")
    
    @staticmethod
    def get_file():
	return _client.get_sys_key('file_path_list')

    @staticmethod
    def get_des_file():                              #获取拖入目标完整路径
	return _client.get_sys_key("des_file_path_list")
    
    @staticmethod
    def get_folder():
	return _client.get_sys_key('folder')