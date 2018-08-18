#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
2017-12-11 deming
2018-02-03 deming 修改---
2018-02-08 deming 修改， task_module 几个with_filter 的方法重写
"""
import os
import sys
import re
import json
import time
import subprocess

G_tw_token_uuid = ""
G_tw_server_ip  = ""
G_tw_account_id = ""
G_tw_account    = ""
G_tw_file_key   = ""
G_tw_http_ip    = ""
G_is_login      = False	
G_bin_path      = os.path.dirname(os.path.dirname(__file__)).replace("\\","/")
G_cgtw_path     = G_bin_path + "/cgtw/"
G_inside_path   = G_bin_path + "/lib/inside"

try:
        sys.path.append(G_inside_path)
        from websocket import create_connection
        import requests
        
except Exception, e:
        raise Exception("Import module fail!")
G_cgtw_session=requests.Session()
class tw:
        __version__="5.2.0"  #当前api版本
        global G_tw_token_uuid
        global G_tw_server_ip
        global G_tw_account_id
        global G_tw_account
        global G_tw_file_key
        global G_tw_http_ip	  #用于python上传下载, 格式: ip:port
        global G_is_login	  #用于判断是否有登录
        global G_cgtw_path	  #cgtw 路径
        
        def __init__(self, T_server_ip=''):
                global G_tw_server_ip	
                global G_tw_token_uuid
                global G_tw_http_ip
                global G_is_login	

                G_tw_server_ip=T_server_ip
                if T_server_ip=='':
                        t_server_ip=tw.local_con._send("main_widget", "get_server_ip", {}, "get")	
                        if isinstance(t_server_ip, bool)!=True and t_server_ip!="":
                                G_tw_server_ip=t_server_ip

                        if G_tw_token_uuid=="":
                                t_token=tw.local_con._send("main_widget", "get_token", {}, "get")	
                                if isinstance(t_token, bool)!=True and t_token!="":
                                        G_tw_token_uuid=t_token
                                        G_is_login=True

                        if G_tw_http_ip=="":
                                t_tw_http_ip=tw.local_con._send("main_widget", "get_server_http", {},"get")
                                if isinstance(t_tw_http_ip, bool)!=True and t_tw_http_ip!="":
                                        G_tw_http_ip=t_tw_http_ip
                else:
                        G_tw_http_ip = T_server_ip
        def get_version(self): 
                return self.__version__
        
        class local_http_con:     #连接qt http 的类

                @staticmethod
                def _send(T_module, T_database, T_action,  T_other_data_dict, T_type="send"): 
                        T_tw_ws=""
                        T_result=""
                        try:
                                T_tw_ws= create_connection("ws://127.0.0.1:64998")
                        except Exception,  e:
                                raise Exception("Cgteamwork client is not login \n"+e)
                        try:				 
                                new_data_dict=dict({"module":T_module, "database":T_database, "action":T_action}.items()+T_other_data_dict.items())				
                                T_tw_ws.send("#@start@#"+json.dumps({"data":new_data_dict, "name":"python",  "type":T_type})+"#@end@#")
                        except Exception,  e:
                                raise Exception("send data to cgteamwork fail \n"+e)
                        else:
                                try:
                                        T_recv=T_tw_ws.recv()
                                        T_tw_ws.close()
                                except Exception,  e:
                                        raise Exception("get data from (127.0.0.1) fail \n"+e)
                                else:
                                        try:
                                                T_dict_data=json.loads(T_recv)
                                        except Exception,  e:
                                                raise(e)
                                        else:
                                                if type(T_dict_data)!=dict:
                                                        raise Exception(T_recv)
                                                else:
                                                        if T_dict_data.has_key('data')==False:
                                                                raise Exception(T_recv)
                                                        else:
                                                                return tw.lib.decode(T_dict_data["data"])

        class local_con:          #连接qt的类

                @staticmethod
                def _send(T_sign, T_method, T_data, T_type="get"): 
                        T_tw_ws=""
                        T_result=""
                        try:
                                T_tw_ws= create_connection("ws://127.0.0.1:64999")
                        except Exception,  e:
                                raise Exception("Cgteamwork client is not login, error:"+str(e))
                        try:
                                T_tw_ws.send(json.dumps(dict({"sign":T_sign, "method":T_method, "type":T_type}.items()+T_data.items())))
                        except Exception,  e:
                                raise Exception(e)
                        else:
                                try:
                                        T_recv=T_tw_ws.recv()
                                        T_tw_ws.close()
                                except Exception,  e:
                                        raise Exception(e)
                                else:
                                        try:
                                                T_dict_data=json.loads(T_recv)
                                        except Exception,  e:
                                                raise Exception(e)
                                        else:
                                                if type(T_dict_data)!=dict:
                                                        raise Exception( T_recv)
                                                else:
                                                        if T_dict_data.has_key('data')==False or T_dict_data.has_key('code')==False :
                                                                raise Exception(T_recv)
                                                        else:
                                                                if T_dict_data['code']=='0':
                                                                        raise Exception( T_dict_data['data'])
                                                                return tw.lib.decode(T_dict_data["data"])

        class con:
                
                @staticmethod
                def _send(a_controller, a_method, a_data_dict):
                        try:
                                global G_tw_http_ip
                                global G_tw_token_uuid
                                t_http_server=G_tw_http_ip    
                                t_token=G_tw_token_uuid
                                a_data_dict["controller"]=a_controller
                                a_data_dict["method"]=a_method
                                t_post_data={"data": json.dumps(a_data_dict)}	
                                req_headers = {"cookie":"token="+t_token}
                                res = G_cgtw_session.post("http://"+t_http_server+"/api.php", data=t_post_data, headers=req_headers)
                        except Exception, e:
                                raise Exception("post data timeout")
                        else:
                                try:
                                        T_dict_data=json.loads(res.text)
                                except Exception,  e:
                                        raise Exception(e)
                                else:
                                        if type(T_dict_data)!=dict:
                                                raise Exception(res)
                                        else:
                                                if T_dict_data.has_key('data')==False or T_dict_data.has_key('code')==False or T_dict_data.has_key('type')==False :
                                                        raise Exception(res)
                                                else:
                                                        if T_dict_data['code']=='0' and T_dict_data['type']=='msg':
                                                                raise Exception(T_dict_data['data'])
                                                        return T_dict_data["data"]                                
                
        class msg:                #消息类
                @staticmethod
                def send_messsage(a_db, a_module, a_moduel_type, a_task_id, account_id_array, a_title="Python Message", a_content=""):
                        if isinstance(a_db, (str, unicode))==False or isinstance(a_module, (str, unicode))==False or  isinstance(a_task_id, (str, unicode))==False or isinstance(account_id_array,list)==False or isinstance(a_title, (str, unicode))==False or isinstance(a_content, (str, unicode))==False or  isinstance(a_moduel_type, (str, unicode))==False:
                                tw.sys().message_error("msg.send_messsage argv error ,there must be (str/unicode, str/unicode, str/unicode, str/unicode, list, str/unicode, str/unicode)")
                        return tw.con._send("c_msg","send_task", {"db":a_db, "module":a_module, "task_id":a_task_id, "account_id_array":account_id_array, "title":a_title, "content":a_content, "module_type":a_moduel_type})
                def send_mail():#没有写
                        pass	

        class sys:

                def _get_uuid(self):
                        if len(sys.argv) < 2 :
                                return ""
                        else:
                                return sys.argv[-1]	

                def __get_argv_data(self):
                        t_dic={"plugin_uuid":self._get_uuid()}
                        return tw.local_con._send("main_widget", "get_plugin_data", t_dic, "get")		

                def get_argv_key(self, T_key, T_argv_data={}):
                        if T_argv_data=={}:
                                T_argv_data=self.__get_argv_data()
                        if type(T_argv_data)==type({}) and T_argv_data.has_key('argv'):
                                if type(T_argv_data['argv'])==type({}) and T_argv_data['argv'].has_key(T_key):
                                        return T_argv_data['argv'][T_key]
                        return False	

                def _get_sys_key(self, T_key):
                        T_argv_data=self.__get_argv_data()
                        if type(T_argv_data)==type({}) and T_argv_data.has_key(T_key):
                                return T_argv_data[T_key]					
                        return False	

                def get_sys_database(self):
                        return self._get_sys_key('database')

                def get_sys_id(self):
                        return self._get_sys_key('id_list')

                def get_sys_link_id(self):
                        return self._get_sys_key('link_id_list')

                def get_sys_module(self):
                        return self._get_sys_key('module')	
                def get_sys_module_type(self):
                        return self._get_sys_key("module_type")
                def get_sys_file(self):
                        return self._get_sys_key('file_path_list')
                def get_sys_des_file(self):                              #获取拖入目标完整路径
                        return self._get_sys_key("des_file_path_list")
                def get_sys_folder(self):
                        return self._get_sys_key('folder')

                def login(self, a_account, a_password, a_http_server=""):#登陆, a_http_server,http服务器地址,如果端口不是80, 需要带端口,例如:192.168.3.110:8686
                        if isinstance(a_account, (str, unicode))==False or isinstance(a_password, (str, unicode))==False or  isinstance(a_http_server, (str, unicode))==False:
                                tw.sys().message_error("sys.login argv error ,there must be (str/unicode, str/unicode)")
                        t_login_data=tw.con._send("c_token", "login", {"account":a_account, "password":a_password, "client_type":"py"})
                        if t_login_data==False:
                                return False
                        global G_tw_token_uuid
                        global G_tw_account_id
                        global G_tw_account
                        global G_tw_file_key	
                        global G_tw_http_ip
                        global G_is_login

                        G_is_login=True
                        G_tw_token_uuid=t_login_data["token"]
                        G_tw_account_id=t_login_data["account_id"]
                        G_tw_account=t_login_data["account"]
                        G_tw_file_key=t_login_data["file_key"]	
                        if a_http_server!="":
                                G_tw_http_ip=a_http_server	
                                
                        return True
                def logout(self):
                        global G_tw_token_uuid
                        G_tw_token_uuid=""

                def get_sys_os(self):
                        import platform
                        t_os=platform.system().lower()
                        if t_os=="windows":
                                return "win"
                        elif t_os=="linux":
                                return "linux"
                        elif t_os=="darwin":
                                return "mac"
                        else:
                                return ""

                def get_account(self):
                        global G_tw_account
                        global G_tw_token_uuid
                        if self.get_is_login()==False:
                                return ""
                        t_account=tw.con._send("c_token", "get_account", {"token":G_tw_token_uuid})
                        return t_account

                def get_account_id(self):
                        global G_tw_account_id	
                        global G_tw_token_uuid
                        if self.get_is_login()==False:
                                return ""
                        t_account_id=tw.con._send("c_token", "get_account_id", {"token":G_tw_token_uuid})
                        return t_account_id

                def get_token(self):
                        global G_tw_token_uuid
                        return G_tw_token_uuid

                def get_server_ip(self): 
                        global	G_tw_server_ip
                        return G_tw_server_ip

                def get_http_server_ip(self):
                        global	G_tw_http_ip
                        return G_tw_http_ip

                def get_is_login(self):
                        global G_tw_token_uuid
                        if G_tw_token_uuid=="":
                                return False
                        return True

                def message_error(self, T_message, T_tile="Error"):
                        raise Exception(T_message)
                
                def set_return_data(self,value="False"):
                        t_dic={"uuid":self._get_uuid(), "result":value}
                        return tw.local_con._send("main_widget", "exec_plugin_result", t_dic, "send")

                def refresh(self, a_database, a_module):
                        pass
                        #if isinstance(a_database, (str, unicode))==False or isinstance(a_module, (str, unicode))==False:
                                #tw.sys().message_error("sys.refresh argv error ,there must be (str/unicode, str/unicode)")
                        #return tw.local_con._send(a_module, a_database, "view_control", "refresh", {}, "send")

                def refresh_select(self, a_database, a_module):
                        pass
                        #if isinstance(a_database, (str, unicode))==False or isinstance(a_module, (str, unicode))==False:
                                #tw.sys().message_error("sys.refresh argv error ,there must be (str/unicode, str/unicode)")
                        #return tw.local_con._send(a_module, a_database, "view_control", "refresh_select", {}, "send")		


                #发送给qt的界面弹出approve或者retake的界面
                def send_to_qc_widget(self, a_database, a_module, a_module_type, a_task_id, a_node_data_dict):#a_node_data_dict为里面一堆的节点的数据，用于更改流程
                        if isinstance(a_database, (str, unicode))==False or isinstance(a_module, (str, unicode))==False or isinstance(a_module_type, (str, unicode))==False or isinstance(a_task_id, (str, unicode))==False  or isinstance(a_node_data_dict, dict)==False:
                                tw.sys().message_error("sys.refresh argv error ,there must be (str/unicode, str/unicode, str/unicode, str/unicode, dict)")
                        return tw.local_http_con._send(a_module, a_database, "send_to_qc_widget",  {"node_data":[a_node_data_dict], "task_id":a_task_id, "module_type":a_module_type})

                def get_status_and_color(self):
                        return tw.con._send("c_status",  "get_status_and_color", {})

        class module:
                s_database="" 
                s_module=""
                s_module_type=""
                s_id_sign=""
                s_id_list=[]

                def __init__(self, a_database, a_module, a_module_type, a_id_list=[]):    #id为task_id     修改   参数需要加一个module_type
                        if isinstance(a_database, (str, unicode))==False or isinstance(a_module, (str, unicode))==False or isinstance(a_module_type, (str, unicode))==False or isinstance(a_id_list, list)==False:
                                raise Exception("module.__init__(str, str, str, list)")                        
                        if a_module_type!="info" and a_module_type!="task":
                                raise Exception("module_type must be info or task")
                        self.s_database=a_database
                        self.s_module=a_module
                        self.s_module_type=a_module_type
                        self.s_id_list=a_id_list
                        self.s_id_sign=self.s_module+".id"
                        if self.s_module_type=="task":
                                self.s_id_sign="task.id"
                        
                        
                def init_with_id(self, a_id):                              #这里可以支持单个ID或者ID列表
                        if isinstance(a_id,  list)==False and isinstance(a_id,  (str, unicode))==False:
                                tw.sys().message_error("module.init_with_id argv error,  (a_id must be list or (str, unicode))")
                        self.s_id_list=[]
                        if isinstance(a_id,  list):
                                self.s_id_list=a_id	
                        elif isinstance(a_id, (str, unicode)):
                                self.s_id_list.append(a_id)	
                        else:
                                self.s_id_list=[]
                        return True
                                

                def init_with_filter(self, a_filter_list, a_limit="5000", a_order_sign_array=[], a_start_num=""):                 #根据filter初始化(ok)
                        self.s_id_list=[]
                        if not isinstance(a_filter_list, list) or isinstance(a_limit, (str, unicode))==False or isinstance(a_order_sign_array, list)==False or isinstance(a_start_num, (str, unicode))==False:
                                tw.sys().message_error("module.init_with_filter argv error,  (a_filter_list must be array,str, array, array)")
                
                        t_data={"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "sign_array":[self.s_id_sign], "sign_filter_array":a_filter_list, "limit":a_limit, "order_sign_array":a_order_sign_array, "start_num":a_start_num}
                        t_data_list=tw.con._send("c_orm", "get_with_filter", t_data)
                        for data in t_data_list:
                                if isinstance(data, list) and len(data)==1:
                                        self.s_id_list.append(data[0])
                        return True

                def get_module(self):                                      #参考以前cgtw.py类
                        return self.s_module

                def get_database(self):                                    #参考以前cgtw.py类
                        return self.s_database

                def get_id_list(self):
                        return self.s_id_list

                def set(self, a_sign_data_dict):                           #使用前需要id_list初始化(ok)
                        if isinstance(a_sign_data_dict, dict)==False:
                                tw.sys().message_error("module argv error , set(dict)")
                        if len(self.s_id_list)<=0:
                                return False      
                        return tw.con._send("c_orm", "set_in_id", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "id_array":self.s_id_list, "sign_data_array":a_sign_data_dict})
                
                def delete(self):                                          #使用前需要id_list初始化(wait)
                        if len(self.s_id_list)<=0:
                                return False   
                        return tw.con._send("c_orm", "del_in_id", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "id_array":self.s_id_list})

                def get_dir(self, a_folder_sign_list):                     #目录标识获取路径, 使用前需要id_list初始化(ok)
                        if isinstance(a_folder_sign_list, list)==False:
                                tw.sys().message_error("module.get_dir argv error ,  (a_folder_sign_list must be array)")
                        if len(self.s_id_list)<=0:
                                return []     
                        t_os=tw.sys().get_sys_os()
                        t_data_list=tw.con._send("c_folder",  "get_replace_path_in_sign", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "task_id_array":self.s_id_list, "os":t_os, "sign_array":a_folder_sign_list})
                        t_result_array=[]

                        for key in t_data_list.keys():
                                t_tmp_dict={}
                                t_tmp_dict["id"]=key
                                for i in range(len(a_folder_sign_list)):
                                        if len(a_folder_sign_list)!=len(t_data_list[key]):
                                                t_tmp_dict[a_folder_sign_list[i]]=""
                                        t_tmp_dict[a_folder_sign_list[i]]=t_data_list[key][i]
                                t_result_array.append(t_tmp_dict)
                        return t_result_array

                def get(self, a_field_sign_list, a_order_list=[]):         #使用前需要id_list初始化 (ok)
                        if isinstance(a_field_sign_list, list)==False or isinstance(a_field_sign_list, list)==False:
                                tw.sys().message_error("module.get_field , argv error(array, array)")
                        t_field_sign_list=[]
                        t_field_sign_list=t_field_sign_list+a_field_sign_list
                        t_field_sign_list.append(self.s_id_sign)
                        if len(self.s_id_list)<=0:
                                return []
                        t_data_list=tw.con._send("c_orm", "get_in_id", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "sign_array":t_field_sign_list, "id_array":self.s_id_list, "order_sign_array":a_field_sign_list})
                        t_result_array=[]
                        for t_data in t_data_list:
                                t_tmp_dict={}
                                n=len(t_field_sign_list)-1
                                for i in range(len(t_field_sign_list)):
                                        t_sign=t_field_sign_list[i]
                                        if len(t_field_sign_list)!=len(t_data):
                                                t_tmp_dict[t_sign]=""
                                                break
                                        if i==n and ".id" in t_sign:
                                                t_sign=t_field_sign_list[i].split(".")[-1].strip()
                                        t_tmp_dict[t_sign]=t_data[i]

                                t_result_array.append(t_tmp_dict)
                        return t_result_array

                def get_field_and_dir(self, a_field_sign_list, a_folder_sign_list):        #使用前需要id_list初始化 (ok)
                        if isinstance(a_field_sign_list, list)==False or isinstance(a_folder_sign_list, list)==False :
                                tw.sys().message_error("module.get_field_and_dir argv error ,  (argv must be (array, array))")
                        if len(self.s_id_list)<=0:
                                return []
                        t_field_data=self.get(a_field_sign_list)
                        t_folder_data=self.get_dir(a_folder_sign_list)
                        if t_field_data==False or t_folder_data==False:
                                tw.sys().message_error("module.get_field_and_dir get data error")
                        t_result_array=[]
                        for t_field in t_field_data:
                                tmp_dict=t_field
                                is_exist=False
                                for t_folder in t_folder_data:
                                        if t_field["id"]==t_folder["id"]:
                                                is_exist=True
                                                tmp_dict.update(t_folder.items())
                                                t_result_array.append(tmp_dict)
                                                break
                                if is_exist==False:
                                        return []
                        else:
                                return t_result_array

                def get_with_filter(self, a_sign_array, a_sign_filter_array, a_limit="5000", a_order_sign_array=[], a_start_num=""): #(ok)
                        if isinstance(a_sign_array, list)==False or isinstance(a_sign_filter_array, list)==False or isinstance(a_limit, (str, unicode))==False or isinstance(a_order_sign_array, list)==False or isinstance(a_start_num, (str, unicode))==False :
                                tw.sys().message_error("module.get_with_filter argv error,  (argvs must be (array, array, str, array, str))")
                        t_sign_array=[]
                        t_sign_array=t_sign_array+a_sign_array
                        t_sign_array.append(self.s_id_sign)
                        t_data_list=tw.con._send("c_orm", "get_with_filter", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "sign_array":t_sign_array, "sign_filter_array":a_sign_filter_array, "limit":a_limit, "order_sign_array":a_order_sign_array, "start_num":a_start_num})
                        if t_data_list==False:
                                tw.sys().message_error("module.get_with_filter get data error")
                        return tw.lib.format_data(t_data_list, t_sign_array)

                def get_image(self, a_field_sign, a_is_small=True):                        #获取图片路径,路径为服务器上的相对路径(ok)
                        if isinstance(a_field_sign,  (str, unicode))==False: 
                                tw.sys().message_error("module.get_image argv error,  (argvs must be (string, unicode))")
                        t_data_list=self.get([a_field_sign])
                        if t_data_list==False:
                                tw.sys().message_error("module.get_image get data error")
                        t_image_data=[]
                        t_size="max"
                        if a_is_small==True:
                                t_size="min"
                        for data in t_data_list:
                                t_image_json=tw.lib.decode(data[a_field_sign])
                                if t_image_json=="":
                                        t_image_data.append({"id":data["id"], a_field_sign:t_image_json})
                                else:
                                        t_image=""
                                        if t_image_json.has_key(t_size):
                                                t_image=t_image_json[t_size]
                                        t_image_data.append({"id":data["id"], a_field_sign:t_image})
                        return t_image_data 

                def download_image(self, a_field_sign, a_is_small=True, a_http_server='', a_local_path=""): #下载图片(ok)
                        if isinstance(a_field_sign,  (str, unicode))==False or isinstance(a_is_small,bool)==False  or isinstance(a_http_server,  (str, unicode))==False  or isinstance(a_local_path,  (str, unicode))==False :
                                tw.sys().message_error("module.get_image argv error,  (argvs must be (string, unicode))")
                        t_os=tw.sys().get_sys_os()
                        t_http_server=a_http_server.strip()
                        if t_http_server=='':
                                global G_tw_http_ip
                                t_http_server=G_tw_http_ip
                        global G_cgtw_path
                        if G_cgtw_path not in sys.path:
                                sys.path.append(G_cgtw_path)
                        from ct import http, com        
                        t_localpath=a_local_path
                        if t_localpath.strip()=="":
                                t_localpath=com().get_tmp_path()
                        if not os.path.exists(t_localpath):
                                try:
                                        os.mkdir(t_localpath)
                                except Exception, e:
                                        tw.sys().message_error(e)
                        t_data_list=self.get([a_field_sign])
                        t_image_data=[]
                        t_size="max"
                        if a_is_small==True:
                                t_size="min"
                        global G_tw_token_uuid
                        t_http=http(t_http_server, G_tw_token_uuid)
                        for data in t_data_list:
                                t_download_list = []
                                t_image_json=tw.lib.decode(data[a_field_sign])
                                if t_image_json != None and isinstance(t_image_json, dict):
                                        for t_image in t_image_json[t_size]:
                                                t_local_file=t_localpath+t_image
                                                t_result=t_http.download(t_image, t_local_file)
                                                if t_result==False:
                                                        t_local_file=""
                                                t_download_list.append(t_local_file)
                                t_image_data.append({"id":data["id"], a_field_sign:t_download_list})
                        return t_image_data  
                def set_image(self, a_field_sign, a_img_path, a_http_server="", a_compress="1080"):     #----20170822----王晨飞 (ok)   增加允许将图片清空
                        a_img_path_list = []
                        if isinstance(a_img_path, (str, unicode))==True:
                                if a_img_path.strip()=="":
                                        return self.set({a_field_sign:""})
                                a_img_path_list.append(a_img_path)
                        else:
                                a_img_path_list = a_img_path
                        if isinstance(a_field_sign, (str, unicode))==False or isinstance(a_img_path_list, (list))==False:
                                tw.sys().message_error("module argv error , set_image(str/unicode, list/str/unicode)")
                        t_http_server=a_http_server.strip()
                        if t_http_server=="":
                                global G_tw_http_ip
                                t_http_server=G_tw_http_ip	
                        t_big_list = []
                        t_small_list = []
                        global G_cgtw_path
                        if G_cgtw_path not in sys.path:
                                sys.path.append(G_cgtw_path)
                        from ct import http
                        global G_tw_token_uuid
                        t_http=http(t_http_server, G_tw_token_uuid)
                        for t_image_file in a_img_path_list:
                                res=t_http.upload_project_img(t_image_file, self.s_database, 'project', None, a_compress)
                                if res.has_key("max") and res.has_key("min"):
                                        t_big_list.append(res["max"])
                                        t_small_list.append(res["min"])
                        return self.set({a_field_sign:tw.lib.encode({"max":t_big_list, "min":t_small_list})})

                def get_count_with_filter(self, a_filter_list):                            #取条数
                        if isinstance(a_filter_list, list)==False:
                                tw.sys().message_error("module.get_count_with_filter argv error,  (a_filter_list must be array")
                        return tw.con._send("c_orm", "get_count_with_filter", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "sign_filter_array":a_filter_list})

                def get_distinct_with_filter(self, a_distinct_sign, a_sign_filter_array, a_order_by_array=[]):       #取消除重复后的结果，一般是单字段
                        if isinstance(a_distinct_sign, (str, unicode))==False or isinstance(a_sign_filter_array, list)==False or isinstance(a_order_by_array, list)==False:
                                tw.sys().message_error("module.get_distinct_with_filter argv error ,  argvs must be (str, array, array)")
                        t_data_list=tw.con._send("c_orm", "get_distinct_with_filter", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "distinct_sign":a_distinct_sign, "sign_filter_array":a_sign_filter_array, "order_sign_array":a_order_by_array})	
                        t_result_array=[]
                        for tmp in t_data_list:
                                t_result_array.append(tmp[0])
                        return t_result_array

        class info_module(module):
                def __init__(self, a_database, a_module, a_id_list=[]):
                        self.s_database=a_database
                        self.s_module=a_module
                        self.s_module_type="info"
                        self.s_id_list=a_id_list
                        self.s_id_sign=self.s_module+".id"

                def create(self, a_sign_data_dict):                  #新增记录(单条), 初始化可以不需要id_list (ok)
                        if isinstance(a_sign_data_dict, dict)==False:
                                tw.sys().message_error("module.create argv error,  (a_sign_data_dict must be dict)")
                        if self.s_module=="asset":
                                a_sign_data_dict=self.__create_asset(a_sign_data_dict)

                        elif self.s_module=="shot":
                                a_sign_data_dict=self.__create_shot(a_sign_data_dict)

                        return tw.con._send("c_orm", "create", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "sign_data_array":a_sign_data_dict})

                def __create_asset(self, a_sign_data_dict): #(ok)
                        if a_sign_data_dict.has_key("asset.asset_name")==False and a_sign_data_dict.has_key("asset.type_name")==False:
                                tw.sys().message_error("info_module.create, a_sign_data_dict must have key (asset.asset_name,  asset.type_name)")
                        t_sign_data_dict=a_sign_data_dict.copy()
                        t_type_id=tw.con._send("c_config","get_one_with_filter", {"table":self.s_database+".conf_type", "field":"#id", "filter_array":[ ["entity_name","=", t_sign_data_dict["asset.type_name"] ] ] })
                        if t_type_id==False  or t_type_id=="":
                                tw.sys().message_error("info_module.create, it's not exist this asset type")
                        t_sign_data_dict.update({"asset.type_name":t_type_id})
                        return t_sign_data_dict
                
                def __create_shot(self, a_sign_data_dict): #(ok)
                        if a_sign_data_dict.has_key("eps.eps_name")==False and a_sign_data_dict.has_key("eps.id")==False and a_sign_data_dict.has_key("shot.shot")==False:
                                tw.sys().message_error("info_module.create, a_sign_data_dict must have key (eps.eps_name/eps.id,  shot.shot)")
                        t_sign_data_dict=a_sign_data_dict.copy()
                        if t_sign_data_dict.has_key("eps.eps_name"):
                                t_eps_id=tw.con._send("c_orm", "get_one_with_filter", {"db":self.s_database, "module":"eps", "module_type":self.s_module_type, "sign":"eps.id", "sign_filter_array":[ ["eps.eps_name", "=", t_sign_data_dict["eps.eps_name"] ] ] })
                                if t_eps_id==False or t_eps_id=="":
                                        tw.sys().message_error("info_module.create, it's not exist this eps" )
                                t_sign_data_dict.pop("eps.eps_name")
                        elif t_sign_data_dict.has_key("eps.id"):
                                t_eps_id=t_sign_data_dict["eps.id"]
                                t_sign_data_dict.pop("eps.id")
                        else:
                                tw.sys().message_error("info_module.create, a_sign_data_dict must have key (eps.eps_name or eps.id)" )
                        t_sign_data_dict.update({"shot.eps_name":t_eps_id})
                        return t_sign_data_dict			

        class task_module(module):
                def __init__(self, a_database, a_module, a_id_list=[]):
                        self.s_database=a_database
                        self.s_module=a_module
                        self.s_id_list=a_id_list
                        self.s_module_type="task"
                        self.s_id_sign="task.id"

                def create_note(self, a_text, a_cc_acount_id="", a_image_list=[], a_http_server=""):          #使用前使用id_list初始化(ok) 修改 增加判断，如果图片列表为空时，不需要http server 
                        if isinstance(a_text, (str,unicode) )==False or isinstance(a_cc_acount_id, (str, unicode))==False or isinstance(a_image_list, list)==False or isinstance(a_http_server, (str, unicode))==False:
                                tw.sys().message_error("module.create_note argv error ,  argvs must be (str, str, list, str)")
                        if len(self.s_id_list)<=0:
                                return False
                        t_http_server=a_http_server.strip()
                        if a_http_server.strip()=="":
                                global G_tw_http_ip
                                t_http_server=G_tw_http_ip
        
                        image_list=[]
                        if len(a_image_list)!=0:
                                global G_tw_token_uuid
                                global G_cgtw_path                        
                                if G_cgtw_path not in sys.path:
                                        sys.path.append(G_cgtw_path) 
                                from ct import http
                                t_http=http(t_http_server, G_tw_token_uuid)                                
                                for t_image_file in a_image_list:
                                        res=t_http.upload_project_img(t_image_file, self.s_database)
                                        if res.has_key("max") and res.has_key("min"):
                                                image_list.append(res)                                
                        t_account_id = tw.sys().get_account_id()
                        return tw.con._send("c_note", "create", {"db":self.s_database, "cc_acount_id":a_cc_acount_id, "field_data_array":{"module":self.s_module,  "module_type":self.s_module_type, "#task_id":",".join(self.s_id_list), "text":{"data":a_text, "image":image_list}, "#from_account_id":t_account_id }})

                def get_note_with_task_id(self, a_field_array):            #使用前使用id_list 初始化 (ok)
                        if isinstance(a_field_array, list)==False:
                                tw.sys().message_error("module.get_note_with_task_id argv error,  (a_field_array must be sarray)")
                        if len(self.s_id_list)<=0:
                                return []
                        t_field_array=[]
                        t_field_array=t_field_array+a_field_array
                        t_field_array.append("#id")
                        t_data_list=tw.con._send("c_note", "get_with_task_id", {"db":self.s_database, "task_id":self.s_id_list[0], "field_array":t_field_array})
                        return tw.lib.format_data(t_data_list, t_field_array)

                def assign_task(self, a_artist_id, a_start_date="", a_end_date=""):                           #使用前使用id_list 初始化(wait)   修改 之前版本不会发送消息 参数由名称改成帐号id
                        if isinstance(a_artist_id, (str, unicode))==False or isinstance(a_start_date, (str, unicode))==False or isinstance(a_end_date, (str, unicode))==False:
                                tw.sys().message_error("module.assign_task argv error ,  (a_artist must be (str, unicode))")
                        if len(self.s_id_list)<=0:
                                return False
                        return tw.con._send("c_work_flow", "assign_to", {'db':self.s_database, 'module':self.s_module, 'module_type':self.s_module_type, 'assign_account_id':a_artist_id, 'start_date':a_start_date, 'end_date':a_end_date, 'task_id_array':self.s_id_list})
                       		

                def submit(self,a_file_path_list, a_note="",a_path_list=[]):#使用前使用id_list 初始化 (ok)
                        if isinstance(a_file_path_list,list)==False or isinstance(a_note,(str,unicode))==False or  isinstance(a_path_list,list)==False:
                                tw.sys().message_error("module.submit argv error isinstance, argvs must be (array,str/unicode,array)")
                        if len(self.s_id_list)<=0:
                                return False
                        if len(a_file_path_list)<=0 and len(a_path_list)<=0 :
                                return False
                        t_note=json.dumps({"data":a_note, "image":[]})
                        if a_note.strip()=="":
                                t_note=""   
                        t_account_id=tw.sys().get_account_id()
                        if a_path_list==[]:
                                a_path_list=a_file_path_list
                        t_submit_file_path_array={"path":a_path_list,"file_path":a_file_path_list}

                        basename_list=[]
                        for n in a_file_path_list:
                                basename_list.append(os.path.basename(n))

                        import uuid
                        version_id=unicode(uuid.uuid4())
                        t_dic={"#link_id":self.s_id_list[0], "version":"",  "filename":basename_list, "local_path":a_path_list, "web_path":[], "sign":"Api Submit", "image":"", "from_version":"", "is_upload_web":"N", "#id":version_id}
                        res=tw.con._send("c_version", "create", {"db":self.s_database, "field_data_array":t_dic})
                        if res!=True:
                                return False
                        return tw.con._send("c_work_flow","submit",{"db":self.s_database,"module":self.s_module,"module_type":self.s_module_type, "task_id":self.s_id_list[0],"account_id":t_account_id,"submit_file_path_array":t_submit_file_path_array,"text":t_note, "version_id":version_id})

                def filebox_get_submit_data(self):
                        if len(self.s_id_list)<=0:
                                return []
                        t_os=tw.sys().get_sys_os()
                        return tw.con._send("c_file","filebox_get_submit_data",{"db":self.s_database,"module":self.s_module,"module_type":self.s_module_type, "task_id":self.s_id_list[0], "os":t_os})

                def create_task(self, a_join_id, a_pipeline_id, a_pipeline_name, a_flow_id='', a_task_name=""):
                        if isinstance(a_join_id, (str, unicode))==False or isinstance(a_pipeline_id, (str, unicode))==False or isinstance(a_pipeline_name, (str, unicode))==False or isinstance(a_flow_id, (str, unicode))==False or isinstance(a_task_name, (str, unicode))==False:
                                tw.sys().message_error("task_module.create_task argv error, create_task(string, string, string, string, string)")
                        t_task_name=a_task_name
                        if t_task_name.strip()=="":
                                t_task_name=a_pipeline_name
                        t_post_data={"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "join_id":a_join_id, "pipeline_id":a_pipeline_id, "flow_id":a_flow_id, "task_name":t_task_name};
                        return tw.con._send("c_orm","create_task", t_post_data)
                
                def get_filebox_with_sign(self, a_filebox_sign): #(ok)
                        if isinstance(a_filebox_sign, (str, unicode))==False:
                                tw.sys().message_error("module.get_filebox_with_sign argv error,  (a_filebox_sign must be (str, unicode))")
                        if len(self.s_id_list)<=0:
                                return []
                        t_os=tw.sys().get_sys_os()
                        return tw.con._send("c_file",  "filebox_get_one_with_sign", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "task_id":self.s_id_list[0], "os":t_os, "sign":a_filebox_sign})


                def get_filebox_with_filebox_id(self, a_filebox_id): #(ok)
                        if isinstance(a_filebox_id, (str, unicode))==False:
                                tw.sys().message_error("module.get_filebox_with_id argv error,  (a_filebox_id must be (str, unicode))")
                        if len(self.s_id_list)<=0:
                                return []
                        t_os=tw.sys().get_sys_os()
                        return tw.con._send("c_file", "filebox_get_one_with_id", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "task_id":self.s_id_list[0], "filebox_id":a_filebox_id, "os":t_os})
                #----------任务模块方法重写--------------
                def init_with_filter(self, a_filter_list, a_limit="5000", a_order_sign_array=[], a_start_num=""):                 #根据filter初始化(ok)
                        self.s_id_list=[]
                        if not isinstance(a_filter_list, list) or isinstance(a_limit, (str, unicode))==False or isinstance(a_order_sign_array, list)==False or isinstance(a_start_num, (str, unicode))==False:
                                tw.sys().message_error("task_module.init_with_filter argv error,  (a_filter_list must be array,str, array, array)")
                        t_filter_list=a_filter_list
                        if len(a_filter_list)!=0:
                                t_filter_list=["(", ["task.module", "=", self.s_module], ")", "and", "("]+a_filter_list+[")"]
                
                        t_data={"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "sign_array":[self.s_id_sign], "sign_filter_array":t_filter_list, "limit":a_limit, "order_sign_array":a_order_sign_array, "start_num":a_start_num}
                        t_data_list=tw.con._send("c_orm", "get_with_filter", t_data)
                        for data in t_data_list:
                                if isinstance(data, list) and len(data)==1:
                                        self.s_id_list.append(data[0])
                        return True
                                
                def get_with_filter(self, a_sign_array, a_sign_filter_array, a_limit="5000", a_order_sign_array=[], a_start_num=""): #(ok)
                        if isinstance(a_sign_array, list)==False or isinstance(a_sign_filter_array, list)==False or isinstance(a_limit, (str, unicode))==False or isinstance(a_order_sign_array, list)==False or isinstance(a_start_num, (str, unicode))==False :
                                tw.sys().message_error("task_module.get_with_filter argv error,  (argvs must be (array, array, str, array, str))")
                        t_sign_array=[]
                        t_sign_array=t_sign_array+a_sign_array
                        t_sign_array.append(self.s_id_sign)
                        t_sign_filter_array=a_sign_filter_array
                        if len(a_sign_filter_array)!=0:
                                t_sign_filter_array=["(", ["task.module", "=", self.s_module], ")", "and", "("]+a_sign_filter_array+[")"]                        
                        t_data_list=tw.con._send("c_orm", "get_with_filter", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "sign_array":t_sign_array, "sign_filter_array":t_sign_filter_array, "limit":a_limit, "order_sign_array":a_order_sign_array, "start_num":a_start_num})
                        if t_data_list==False:
                                tw.sys().message_error("task_module.get_with_filter get data error")
                        return tw.lib.format_data(t_data_list, t_sign_array)
                
                def get_count_with_filter(self, a_filter_list):                            #取条数
                        if isinstance(a_filter_list, list)==False:
                                tw.sys().message_error("task_module.get_count_with_filter argv error,  (a_filter_list must be array")
                        t_filter_list=a_filter_list
                        if len(a_filter_list)!=0:
                                t_filter_list=["(", ["task.module", "=", self.s_module], ")", "and", "("]+a_filter_list+[")"]                        
                        return tw.con._send("c_orm", "get_count_with_filter", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "sign_filter_array":t_filter_list})

                def get_distinct_with_filter(self, a_distinct_sign, a_sign_filter_array, a_order_by_array=[]):       #取消除重复后的结果，一般是单字段
                        if isinstance(a_distinct_sign, (str, unicode))==False or isinstance(a_sign_filter_array, list)==False or isinstance(a_order_by_array, list)==False:
                                tw.sys().message_error("task_module.get_distinct_with_filter argv error ,  argvs must be (str, array, array)")
                        t_sign_filter_array=a_sign_filter_array
                        if len(a_sign_filter_array)!=0:
                                t_sign_filter_array=["(", ["task.module", "=", self.s_module], ")", "and", "("]+a_sign_filter_array+[")"]  
                        #print t_sign_filter_array
                        t_data_list=tw.con._send("c_orm", "get_distinct_with_filter", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "distinct_sign":a_distinct_sign, "sign_filter_array":t_sign_filter_array, "order_sign_array":a_order_by_array})	
                        t_result_array=[]
                        for tmp in t_data_list:
                                t_result_array.append(tmp[0])
                        return t_result_array                
                def update_flow(self, a_field_sign, a_status, a_note=""):
                        if isinstance(a_field_sign, (str, unicode))==False or isinstance(a_note, (str, unicode))==False or isinstance(a_status, (str, unicode))==False:
                                tw.sys().message_error("task_module.get_distinct_with_filter argv error ,  argvs must be (str, str, str)")                        
                        if len(self.s_id_list)<=0:
                                return False
                        t_note_data=""
                        if a_note.strip()!="":
                                t_note_data=json.dumps({"data":a_note, "image":[]})
                        return  tw.con._send("c_work_flow","python_update_flow", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type,  "field_sign":a_field_sign, "text":t_note_data, "status":a_status, "task_id":self.s_id_list[0]})

        class filebox:
                s_database=""

                def __init__(self, a_database):
                        self.s_database=a_database

                def get_with_id(self, a_filebox_id):                        #取单条记录
                        if isinstance(a_filebox_id, (str, unicode))==False :
                                tw.sys().message_error("filebox.get_with_id argv error,  (a_filebox_id must be (str, unicode))")
                        return tw.con._send("c_file", "get_one_with_id", {"db":self.s_database, "id":a_filebox_id, "field_array":["#pipeline_id", "title"]})

                def get_with_filter(self, a_filter_list, a_field_list): 
                        if isinstance(a_filter_list, list)==False or isinstance(a_field_list, list)==False:
                                tw.sys().message_error("filebox.get_with_filter argv error,  (argvs must be (array, array)")
                        t_field_list=[]
                        t_field_list=t_field_list+a_field_list
                        t_field_list.append("#id")
                        t_data_list=tw.con._send("c_file", "get_with_filter", {"db":self.s_database, "filter_array":a_filter_list, "field_array":t_field_list})
                        return tw.lib.format_data(t_data_list, t_field_list)

                def get_with_pipeline_id(self, a_pipeline_id, a_module):  
                        if isinstance(a_pipeline_id, (str, unicode))==False or isinstance(a_module, (str, unicode))==False:
                                tw.sys().message_error("filebox.get_with_pipeline_id argv error ,  (argvs must be (str, (str, unicode))")
                        return self.get_with_filter([ [ "#pipeline_id", "in", [a_pipeline_id, "all"] ], "and", [ "module", "=", a_module ] , "and", [ "module_type", "=", "task"]], ["title", "#id"]);

        class plugin:

                def get_with_id(self, a_field, a_id):
                        if isinstance(a_field, (list, str, unicode))==False or isinstance(a_id, (str, unicode))==False:
                                tw.sys().message_error("plugin.get_with_id argv error,  (argvs must be (str/array, str/unicode))")
                        t_field=[]
                        if isinstance(a_field,list):
                                t_field=t_field+a_field
                        elif isinstance(a_field,(str,unicode)):
                                t_field.append(a_field)

                        t_field.append("#id")
                        t_data_list=tw.con._send("c_plugin", "get_one_with_id", {"id":a_id, "field_array":t_field})
                        return tw.lib.format_data_to_dict(t_data_list, t_field)

                def get_with_filter(self, a_field_list, a_filter_list):
                        if isinstance(a_filter_list, list)==False or isinstance(a_field_list, list)==False:
                                tw.sys().message_error("plugin.get_with_filter argv error , (argvs must be (array, array))")
                        t_field_list=[]
                        t_field_list=t_field_list+a_field_list
                        t_field_list.append("#id")
                        t_data_list=tw.con._send("c_plugin", "get_with_filter", {"field_array":t_field_list, "filter_array":a_filter_list})
                        return tw.lib.format_data(t_data_list, t_field_list)

                def get_with_type(self, a_field_list, a_type):              #nuke, maya之类的类型
                        if isinstance(a_field_list, list)==False or isinstance(a_type, (str, unicode))==False:
                                tw.sys().message_error("plugin.get_with_type  argv error , (argvs must be (array, (str, unicode)))")
                        t_field_list=[]
                        t_field_list=t_field_list+a_field_list			
                        t_field_list.append("#id")
                        t_data_list=tw.con._send("c_plugin", "get_with_type", {"type":a_type, "field_array":t_field_list})
                        return tw.lib.format_data(t_data_list, t_field_list)

                def get_argvs_with_id(self, a_plugin_id):
                        if isinstance(a_plugin_id,(str,unicode))==False:
                                tw.sys().message_error("plugin.get_argvs_with_id argv error, argv must be str/unicode")
                        t_data_list=self.get_with_id("argv",a_plugin_id)
                        if t_data_list==False:
                                tw.sys().message_error("plugin.get_argvs_with_id get data error")
                        t_argv=tw.lib.decode(t_data_list['argv'])
                        if t_argv=="":
                                return []
                        t_result_dict={}
                        for key in t_argv.keys():
                                t_result_dict[key]=t_argv[key]["value"]
                        return t_result_dict

                def set_argvs_with_id(self, a_plugin_id, a_argvs_dict):
                        if isinstance(a_plugin_id,(str,unicode))==False or isinstance(a_argvs_dict,dict)==False:
                                tw.sys().message_error("plugin.set_argvs_with_id argv error, argvs must be (str/unicode,dict))")
                        t_argv_dict=self.__change_data_dict_for_set_argvs(a_argvs_dict)
                        if t_argv_dict==False:
                                return False
                        t_json_str=tw.lib.encode(t_argv_dict)
                        if t_json_str==False:
                                return False
                        return tw.con._send("c_plugin","set_one_with_id",{"id":a_plugin_id,"field_data_array":{"argv":t_json_str}})

                def __change_data_dict_for_set_argvs(self,a_argvs_dict):
                        if isinstance(a_argvs_dict,dict)==False:
                                tw.sys().message_error("plugin.__change_data_dict_for_set_argvs argv error , argv must be dict")
                        t_result_dict={}
                        for key in a_argvs_dict.keys():
                                t_result_dict[key]={"value":a_argvs_dict[key],"description":""}
                        return t_result_dict

        class pipeline:
                s_database=""

                def __init__(self, a_database):
                        self.s_database=a_database

                def get_with_module(self, a_module, a_field_list):
                        if isinstance(a_field_list, list)==False:
                                tw.sys().message_error("pipeline.get_with_module argv error, (a_field_list must be array)")
                        t_new_field_list = []
                        for field in a_field_list:
                                if field != "name":
                                        t_new_field_list.append(field)  
                                else:
                                        t_new_field_list.append("entity_name")
                        t_field_list=[]
                        t_field_list=t_field_list+t_new_field_list
                        t_field_list.append("#id")
                        t_data_list=tw.con._send("c_pipeline", "get_with_module", {"db":self.s_database, "module":a_module, "module_type":"task", "field_array":t_field_list})
                        t_res = tw.lib.format_data(t_data_list, t_field_list)
                        t_name_res = []
                        for t_datalist in t_res:
                                if t_datalist.has_key("entity_name"):
                                        t_datalist["name"]=t_datalist["entity_name"]
                                        t_datalist.pop("entity_name")
                                t_name_res.append(t_datalist)
                        return t_name_res
                def get_with_filter(self, a_field_list, a_filter_list):
                        if isinstance(a_field_list, list)==False or isinstance(a_filter_list, list)==False:
                                tw.sys().message_error("pipeline.get_with_filter argv error ,  (agrvs must be (array, array))")
                        t_new_field_list = []
                        for field in a_field_list:
                                if field != "name":
                                        t_new_field_list.append(field)  
                                else:
                                        t_new_field_list.append("entity_name")
                        for filters in a_filter_list:
                                if filters[0]=="name":
                                        filters[0]="entity_name"                        
                        t_field_list=[]
                        t_field_list=t_field_list+t_new_field_list
                        t_field_list.append("#id")
                        t_data_list=tw.con._send("c_pipeline", "get_with_filter", {"db":self.s_database, "field_array":t_field_list, "filter_array":a_filter_list})
                        t_res = tw.lib.format_data(t_data_list, t_field_list)
                        t_name_res = []
                        for t_datalist in t_res:
                                if t_datalist.has_key("entity_name"):
                                        t_datalist["name"]=t_datalist["entity_name"]
                                        t_datalist.pop("entity_name")
                                t_name_res.append(t_datalist)
                        return t_name_res                

        class history:
                s_database=""
                s_module=""
                def __init__(self, a_database, a_module, a_module_type):
                        self.s_database=a_database			
                        self.s_module=a_module
                        self.s_module_type=a_module_type

                def get_with_filter(self, a_field_list, a_filter_list):
                        if isinstance(a_filter_list, list)==False or isinstance(a_field_list, list)==False:
                                tw.sys().message_error("history.get_with_filter argv error ,  (argvs must be (array, array)")
                        t_field_list=[]
                        t_field_list=t_field_list+a_field_list			
                        t_field_list.append("#id")
                        t_data_list=tw.con._send("c_history", "get_with_filter", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type,"filter_array":a_filter_list, "field_array":t_field_list})
                        return tw.lib.format_data(t_data_list, t_field_list)

                def count_with_filter(self, a_filter_list):
                        if isinstance(a_filter_list, list)==False:
                                tw.sys().message_error("history.count_with_filter argv error,  (a_filter_list must be array)")
                        return tw.con._send("c_history", "count_with_filter", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "filter_array":a_filter_list})

        class link:
                s_database=""
                s_module=""
                s_id_list=[]
                def __init__(self, a_database, a_module, a_module_type):
                        self.s_database=a_database
                        self.s_module=a_module
                        self.s_module_type=a_module_type

                def link_asset(self, a_id_list ,a_link_id_list):
                        if isinstance(a_link_id_list, list)==False or isinstance(a_id_list, list)==False:
                                tw.sys().message_error("link.link_asset argv error, link_asset(array, array)")
                        if len(a_id_list)<=0:
                                tw.sys().message_error("a_id_list keyin error !!! like this [1,2,3]")
                        
                        return tw.con._send("c_many2many", "add_link", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "module_tab_id_array":a_id_list, "link_module":"asset", "link_module_tab_id_array":a_link_id_list, "is_main":"Y"})

                def unlink_asset(self, a_id_list, a_link_id_list):
                        if isinstance(a_link_id_list, list)==False or (isinstance(a_id_list, list)==False and isinstance(a_id_list, (str, unicode))==False):
                                tw.sys().message_error("link.unlink_asset argv error, link_asset(array, array/str/unicode)")
                        t_id_list=a_id_list
                        if isinstance(t_id_list, (str, unicode))==True:
                                t_id_list=[t_id_list]
                        return tw.con._send("c_many2many", "remove_link", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "module_tab_id_array":t_id_list, "link_module":"asset", "link_module_tab_id_array":a_link_id_list, "is_main":"Y"})

                def get_link_asset(self, a_id):
                        if isinstance(a_id, (str, unicode))==False:
                                tw.sys().message_error("link.unlink_asset argv error, link_asset(str/unicode)")
                        return tw.con._send("c_many2many", "get_link", {"db":self.s_database, "module":self.s_module, "module_type":self.s_module_type, "module_tab_id":a_id, "link_module":"asset","is_main":"Y"})

        class lib:

                @staticmethod
                def _is_json(value):
                        try:
                                eval(value)
                        except Exception, e:
                                pass
                                return False
                        else:
                                return True

                @staticmethod
                def decode(value):#json_decode
                        if tw.lib._is_json(value):
                                return json.loads(value)
                        else:
                                return value		

                @staticmethod
                def encode(value):#json_encode
                        if isinstance(value,dict):
                                try:
                                        json_str=json.dumps(value)
                                        return json_str
                                except Exception,e:
                                        raise Exception(e)
                        else:
                                return False

                @staticmethod
                def format_data_to_dict(a_data_list, a_sign_list):#返回值为单层array, 用于get_one
                        if isinstance(a_data_list, list)==False or isinstance(a_sign_list, list)==False:
                                tw.sys().message_error("lib.format_data argv error, format_data_to_dict(list, list)")                        
                        if len(a_data_list)!=len(a_sign_list):
                                tw.sys().message_error("lib.format_data_to_dict data error , (a_data_list's length is not equal to a_sign_list's)")
                        t_result_dict={}
                        n=len(a_data_list)-1
                        for i in range(len(a_data_list)):
                                t_sign=a_sign_list[i].replace("#", "")
                                if i==n and ".id" in a_sign_list[i]:
                                        t_sign=a_sign_list[i].split(".")[-1].strip()
                                t_result_dict[t_sign]=a_data_list[i]
                        return t_result_dict

                @staticmethod
                def format_data(a_data_list, a_sign_list):#多层
                        if isinstance(a_data_list, list)==False or isinstance(a_sign_list, list)==False:
                                tw.sys().message_error("lib.format_data argv error, format_data(list, list)")
                        t_result_array=[]
                        for data in a_data_list:
                                t_tmp_dict=tw.lib.format_data_to_dict(data, a_sign_list)
                                if t_tmp_dict==False:
                                        tw.sys().message_error("lib.format_data data error")
                                t_result_array.append(t_tmp_dict)
                        return t_result_array




        class software:

                def __init__(self, a_db):
                        self.s_db = a_db
                        
                def get_software_type(self): # 取软件分类
                        return tw.con._send("c_software", "get_software_type", {"db":self.s_db})
                        
                def get_software_path(self, a_name):
                        if isinstance(a_name, (str,unicode))==False:
                                tw.sys().message_error("software.get_software_path argv error, get_software_path(string/unicode)")
                        return tw.con._send("c_software", "get_software_path", {"db":self.s_db, "name":a_name})
                def get_software_with_type(self, a_type): #根据类型获取软件路径, 如果有多个, 获取第一个
                        if isinstance(a_type, (str,unicode))==False:
                                tw.sys().message_error("software.get_software_path argv error, get_software_path(string/unicode)")
                        return tw.con._send("c_software", "get_software_with_type", {"db":self.s_db, "type":a_type})         
        class api_data:

                def __init__(self, a_db):
                        if isinstance(a_db, (str,unicode))==False:
                                tw.sys().message_error("api_data.__init__, argv error(string/unicode)")
                        self.s_db = a_db

                def set_value(self, a_key, a_value, a_is_user=True):
                        if isinstance(a_key, (str,unicode))==False or isinstance(a_value, (str,unicode))==False or isinstance(a_is_user, bool)==False:
                                tw.sys().message_error("api_data.set_value , argv error(string/unicode, string/unicode, bool)")
                        t_method="set_common"
                        if a_is_user==True:
                                t_method="set_user"
                        return tw.con._send("c_api_data", t_method, {"db":self.s_db, "key":a_key, "value":a_value})

                def get_key(self, a_key, a_is_user=True):
                        if isinstance(a_key, (str,unicode))==False or isinstance(a_is_user, bool)==False:
                                tw.sys().message_error("api_data.get_key , argv error(string/unicode, bool)")
                        t_method="get_common"
                        if a_is_user==True:
                                t_method="get_user"
                        return tw.con._send("c_api_data", t_method, {"db":self.s_db, "key":a_key})


        class queue:
                def __init__(self):
                        self.s_machine_info={"mac":"", "hostname":"", "ip":""}
                        import uuid
                        mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
                        self.s_machine_info["mac"]=mac
                        import socket
                        hostname = socket.gethostname() 
                        self.s_machine_info["hostname"]=hostname
                        ip = socket.gethostbyname(hostname) 
                        self.s_machine_info["ip"]=ip                        
                        
                def submit(self, a_field_data_array):
                        if isinstance(a_field_data_array, dict)==False:
                                tw.sys().message_error("queue.sumbit argv error, submit(dict)");
                        return tw.con._send("c_queue", "submit", {"field_data":a_field_data_array})
                        
                def get_task(self, a_type):
                        if isinstance(a_type, (str, unicode))==False:
                                tw.sys().message_error("queue.get_task argv error, get_task(str)")
                        return tw.con._send("c_queue", "get_task", {"machine_info":self.s_machine_info, "type":a_type})
 
                def work(self, a_task_id):
                        if isinstance(a_task_id, (str, unicode))==False:
                                tw.sys().message_error("queue.work argv error, work(str/unicode)")
                        return tw.con._send("c_queue", "work", {"mac":self.s_machine_info["mac"], "task_id":a_task_id})

                def finish(self, a_task_id):
                        if isinstance(a_task_id, (str, unicode))==False:
                                tw.sys().message_error("queue.finish argv error, finish(str/unicode)")
                        return tw.con._send("c_queue", "finish", {"mac":self.s_machine_info["mac"], "task_id":a_task_id})
                def error(self, a_task_id): #任务数据不正确
                        if isinstance(a_task_id, (str, unicode))==False:
                                tw.sys().message_error("queue.error argv error, error(str/unicode)")
                        return tw.con._send("c_queue", "error", {"mac":self.s_machine_info["mac"], "task_id":a_task_id})                        
                
                def get_task_status(self, a_task_id):
                        if isinstance(a_task_id, (str, unicode))==False:
                                tw.sys().message_error("queue.get_task_status argv error, get_task_status(str/unicode)")
                        return tw.con._send("c_queue", "get_task_status", {"task_id":a_task_id})                        
        
        class version:
                def __init__(self, a_db):
                        if isinstance(a_db, (str,unicode))==False:
                                tw.sys().message_error("version.__init__, argv error(string/unicode)")
                        self.s_db = a_db
        
                def get_with_filter(self, a_field_list, a_filter_list):
                        if isinstance(a_filter_list, list)==False or isinstance(a_field_list, list)==False:
                                tw.sys().message_error("version.get_with_filter argv error ,  (argvs must be (array, array)")
                        t_field_list=[]
                        t_field_list=t_field_list+a_field_list			
                        t_field_list.append("#id")
                        t_data_list=tw.con._send("c_version", "get_with_filter", {"db":self.s_db, "filter_array":a_filter_list, "field_array":t_field_list})
                        return tw.lib.format_data(t_data_list, t_field_list)
        
                def create(self, a_link_id,  a_version, a_local_path="", a_web_path="", a_sign="", a_image="", a_from_version=""):
                        if isinstance(a_link_id, (str,unicode))==False or isinstance(a_version, (str,unicode))==False or \
                                   isinstance(a_local_path, (str,unicode))==False or   isinstance(a_web_path, (str,unicode))==False or  isinstance(a_sign, (str,unicode))==False or \
                                isinstance(a_from_version, (str,unicode))==False :
                                tw.sys().message_error("version.create, argv error(unicode, unicode, unicode,unicode, unicode, unicode, unicode,unicode)")
                        t_filename=[]
                        t_basename=os.path.basename(a_local_path)
                        if t_basename.strip()!="":
                                t_filename=[t_basename]
                        t_webpath=[]
                        if a_web_path.strip()!="":
                                t_webpath=[a_web_path]
                        t_localpath=[]
                        if a_local_path.strip()!="":
                                t_localpath=[a_local_path]
                        is_upload_web="N"
                        if len(t_webpath)!=0:
                                is_upload_web="Y"
                        t_dic={"#link_id":a_link_id, "version":a_version,  "filename":t_filename, "local_path":t_localpath, "web_path":t_webpath, "sign":a_sign, "image":a_image, "from_version":a_from_version, "is_upload_web":is_upload_web}
                        return self._create(t_dic)
        
        
                def _create(self, a_field_data_dic):
                        if isinstance(a_field_data_dic, dict)==False:
                                tw.sys().message_error("version.create, argv error(dict)")
                        return tw.con._send("c_version", "create", {"db":self.s_db, "field_data_array":a_field_data_dic})
        
                def get_field(self):
                        return tw.con._send("c_version", "get_field", {})                
        class link_entity:
                def get_entity_name(self, a_db, a_link_id):
                        if isinstance(a_db, (str, unicode))==False or isinstance(a_link_id, (str, unicode, list))==False:
                                tw.sys().message_error("link_entity.get_entity_name argv error(str/unicode, str/unicode/list)")                        
                        return tw.con._send("c_link_entity", "get_entity_name", {"db":a_db, "link_id":a_link_id})
                
                def get_entity_name_with_filter(self, a_db, a_filter_list):
                        if isinstance(a_db, (str, unicode))==False or isinstance(a_filter_list, list)==False:
                                tw.sys().message_error("link_entity.get_with_filter argv error(str/unicode, list)")                        
                        return tw.con._send("c_link_entity", "get_with_filter", {"db":a_db, "filter_array":a_filter_list})                    
if __name__ == "__main__":
        #print tw().get_version()
        t_tw = tw("192.168.199.88")
        t_tw.sys().login("deming", "111111")
        print t_tw.module('proj_dm', 'shot', 'info', ["508767AD-1062-34EF-D25F-5ADBA91568E0"]).set_image("shot.image", r"C:\Users\Administrator\Desktop\4K\1FPQ04432-3.jpg", "")
        #t_task_module=t_tw.task_module("proj_dm", "shot", ["506FF024-8F0C-D3A5-4782-AB1DA8682108"])
        #print t_task_module.update_flow("task.leader_status", "approve", "aaaa")
        #print t_tw.msg.send_messsage("proj_dm", "shot", "task", '56822BA4-4E3C-677F-AE1D-EE7AB184687A', ['2636F64C-10A6-DBCF-FCBA-8BB76ED2311A'], "Python", u"Python 托尔斯泰")
        #print t_tw.link_entity().get_entity_name("proj_dm", "506FF024-8F0C-D3A5-4782-AB1DA8682108")    
        #print t_tw.link_entity().get_entity_name("proj_dm", ["506FF024-8F0C-D3A5-4782-AB1DA8682108", "79E07F1F-FB71-D0F4-4F5E-2BD5B59B8837"])
        #print t_tw.link_entity().get_entity_name_with_filter("proj_dm", [[ "#link_id", "in", ["506FF024-8F0C-D3A5-4782-AB1DA8682108", "79E07F1F-FB71-D0F4-4F5E-2BD5B59B8837"]]])
        #t_tw = tw('192.168.199.95')
        #t_tw.sys().login("deming", "")
        #t_res=t_tw.module("proj_dm", "shot", "task").get_with_filter(["eps.eps_name", "shot.shot"], [ [ "eps.eps_name", "has", "%"]], "1", ["eps.eps_name", "shot.shot"], "0")
        #t_module=t_tw.module("proj_dm", "shot", "task")
        #t_module.init_with_filter( [ [ "eps.eps_name", "has", "%"]], "1", ["task.id"], "2")
        #print t_module.get_id_list()
        #-----------------------------------info module--------------------------
        #t_asset=t_tw.info_module("proj_dm", "asset")
        #t_asset.init_with_filter([ ["asset.asset_name", "has", "%"], "and",["asset.type_name", "=", "chars"]])
        #print t_asset.get(["asset.asset_name", "asset.type_name"])                
        #print t_asset.get_dir(["mod_check"])
        #print t_asset.get_field_and_dir(["asset.asset_name", "asset.type_name"], ["mod_check"])
        #print t_asset.get_with_filter(["asset.asset_name", "asset.type_name"], [ ["asset.type_name", "=", "chars"]])
        #print t_asset.get_image("asset.image")
        #print t_asset.set_image("asset.image", "/Users/Air/Downloads/123123.jpg", "192.168.199.95")
        #print t_asset.get_image("asset.image", False)
        #print t_asset.download_image("asset.image", False, "192.168.199.95", "/Users/Air/Downloads/")
        #print t_asset.create({"asset.asset_name":"duck_1", "asset.type_name":"chars"});
        #t_shot=t_tw.info_module("proj_dm", "shot")
        #print t_shot.create({"eps.eps_name":"E002", "shot.shot":"Sc005"})
        
        #-----------------------------------task module--------------------------
        
        #t_task_module=t_tw.task_module("proj_dm", "shot", ["5D6453D5-6A2F-AAE0-F3AA-2E42651A4C6D"])
        #t_task_module=t_tw.task_module("proj_dm", "asset")
        #print len(t_task_module.get_with_filter(["task.module"], [["task.module", "has", "%"]]))
        #print t_task_module.get_count_with_filter( [["task.module", "has", "%"]])
        #print t_task_module.get_distinct_with_filter("task.module", [["task.module", "has", "%"]])
        #print t_task_module.init_with_filter([ ["asset.asset_name", "has", "%"]])
        #print t_task_module.get(["task.pipeline", "task.module"])
        #print t_task_module.get_id_list()
        #print t_task_module.get_filebox_with_sign("maya_work");
        #print t_task_module.get_filebox_with_filebox_id("5827F4A3-F858-EB35-ADF9-76BCD287560A");
        #print t_task_module.get(["asset.asset_name", "asset.type_name", "task.pipeline"])
        #print t_task_module.get_dir(["mod_check"])
        #print t_task_module.get_field_and_dir(["asset.asset_name", "asset.type_name", "task.pipeline"], ["mod_check"])
        #print t_task_module.get_with_filter(["asset.asset_name", "asset.type_name", "task.pipeline"], [ ["asset.type_name", "=", "chars"], "and", ["task.pipeline", "=", "Mod"]])
        #print t_task_module.get_image("task.image")
        #print t_task_module.set_image("task.image", "/Users/Air/Downloads/a0dfe2eedaa9eb25f4212d4c2b666a3e.jpg", "192.168.199.95")
        #print t_task_module.set({"task.image":""})
        #print t_task_module.get_image("task.image", False)
        #print t_task_module.download_image("task.image", True, "192.168.199.95")
        #print t_task_module.create_note("Create Note Test With Image", "2636F64C-10A6-DBCF-FCBA-8BB76ED2311A", ["/Users/Air/Downloads/a0dfe2eedaa9eb25f4212d4c2b666a3e.jpg"], "192.168.199.95")
        #print t_task_module.create_note("Create Note Test Without Image", "2636F64C-10A6-DBCF-FCBA-8BB76ED2311A")
        #print t_task_module.get_note_with_task_id(["text"])
        #print t_task_module.assign_task("2636F64C-10A6-DBCF-FCBA-8BB76ED2311A", "2017-12-11", "2017-12-25")
        #print t_task_module.submit(['/Users/Air/Downloads/a0dfe2eedaa9eb25f4212d4c2b666a3e.jpg'], "Submit")
        #print t_task_module.submit(['/Users/Air/Downloads/a0dfe2eedaa9eb25f4212d4c2b666a3e.jpg'], "Submit")
        #print t_task_module.filebox_get_submit_data()
        #print t_task_module.delete()
        #print t_task_module.create_task("F3ECFC93-5339-D1A5-168D-4EA94A0D3299", "27337D30-72E2-2563-9AFB-9FA73D6A9784", "Design", '', "aaaa" )
        
        #-----------------------------------filebox----------------------------
        
        #t_filebox=t_tw.filebox("proj_dm")
        #print t_filebox.get_with_id("5827F4A3-F858-EB35-ADF9-76BCD287560A")
        #print t_filebox.get_with_pipeline_id("27337D30-72E2-2563-9AFB-9FA73D6A9784", "asset")

        #-----------------------------------pipeline----------------------------
        #t_pipeline=t_tw.pipeline("proj_dm")
        #print t_pipeline.get_with_module("asset", ["entity_name", "#id", "module"])
        
        #-----------------------------------link----------------------------
        #t_link=t_tw.link("proj_dm", "shot", "info")
        #print t_link.get_link_asset("25EFD7C2-AFF0-9C2F-35F8-FA29192BFC0D")
        #print t_link.unlink_asset("25EFD7C2-AFF0-9C2F-35F8-FA29192BFC0D", ["2EDED265-357F-AF52-ECB9-389269A2DF8F"])
        #print t_link.get_link_asset("25EFD7C2-AFF0-9C2F-35F8-FA29192BFC0D")
        #print t_link.link_asset( ["25EFD7C2-AFF0-9C2F-35F8-FA29192BFC0D"], ["2EDED265-357F-AF52-ECB9-389269A2DF8F"])
        
        #t_link=t_tw.link("proj_dm", "shot", "task")
        #print t_link.get_link_asset("2AA8C016-4547-0644-F712-441AFBEA4EFF")
        #print t_link.unlink_asset(["2AA8C016-4547-0644-F712-441AFBEA4EFF", "E94619B5-A49A-3490-7060-C0965F7BF6F0"], ["04DC7197-6565-D742-3817-47729CAD4DDB"])
        #print t_link.get_link_asset("2AA8C016-4547-0644-F712-441AFBEA4EFF")
        #print t_link.link_asset(["2AA8C016-4547-0644-F712-441AFBEA4EFF", "E94619B5-A49A-3490-7060-C0965F7BF6F0"], ["04DC7197-6565-D742-3817-47729CAD4DDB", "2024D874-F919-782E-15D8-C5D81AC9FA67"])
       
        #------------------------------------software-------------------------
        #t_software=t_tw.software("proj_dm")
        #print t_software.get_software_type()
        #print t_software.get_software_path("maya2015")
        
        #-----------------------------------version---------------------------
        #version=t_tw.version('proj_dm')
        #print version.get_with_filter(["sign", "filename"], [ [ "#link_id", "=", "9360EFC5-AFF5-BA43-4C46-75E0CD95CA4B"]])
        #print version.create("44E93EDA-9A68-158D-D0CB-A1EB95BFD080", "v002", "/usr/temp/aaa.txt",  "/upload/usr/temp/aadfafadf.txt",  "JKJJ", "","v001")
        #print version.get_field()