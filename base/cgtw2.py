#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
2018-06-25 shiming
"""
import os
import sys
import re
import json
import time
import subprocess

G_tw_token = ""
G_tw_account_id = ""
G_tw_account    = ""
G_tw_file_key   = ""
G_tw_http_ip    = ""
G_is_login      = False	
G_bin_path      = os.path.dirname(os.path.dirname(__file__)).replace("\\","/")
#G_bin_path      = u"c:/cgteamwork/bin"
G_cgtw_path     = G_bin_path + "/cgtw/"
G_inside_path   = G_bin_path + "/lib/inside"

try:
    sys.path.append(G_inside_path)
    from websocket import create_connection
    import requests

except Exception, e:
    raise Exception("Import module(websocket, requests) fail")

from twlib._con import _con
from twlib._con_local import _con_local
from twlib._client import _client
from twlib._module import _module

G_cgtw_session=requests.Session()
class tw:
    __version__="5.2.0"  #当前api版本
    global G_tw_token
    global G_tw_account_id
    global G_tw_account
    global G_tw_file_key
    global G_tw_http_ip	  #用于python上传下载, 格式: ip:port
    global G_is_login	  #用于判断是否有登录
    global G_cgtw_path	  #cgtw 路径

    def __init__(self, a_http_ip='', a_account='', a_password=''):
        u"""
         描述: 初始化, 备注:服务器IP,账号,密码都不填写的时候,会连接到客户端获取登陆信息
         调用: __init__(a_http_ip='', a_account='', a_password='')
              ---> a_http_ip                   服务器IP, (str/unicode)
              ---> a_account                   账号 (str/unicode)
              ---> a_password                  密码 (str/unicode)
         """           
        global G_tw_token
        global G_tw_http_ip
        global G_is_login	
        global G_tw_file_key
        global G_tw_account_id
        global G_tw_account        
        
        if unicode(a_http_ip).strip()!="" and unicode(a_account).strip()!="":
            G_tw_http_ip=a_http_ip
            t_login_data=tw.send_web("c_token", "login", {"account":a_account, "password":a_password, "client_type":"py"})
            if t_login_data==False:
                raise Exception("tw.Login fail")
        
            G_is_login=True
            G_tw_token=t_login_data["token"]
            G_tw_account_id=t_login_data["account_id"]
            G_tw_account=t_login_data["account"]
            G_tw_file_key=t_login_data["file_key"]
            
        else:
            if G_tw_http_ip=="":
                t_tw_http_ip=tw.send_local_socket("main_widget", "get_server_http", {},"get")
                if isinstance(t_tw_http_ip, bool)!=True and t_tw_http_ip!="":
                    G_tw_http_ip=t_tw_http_ip  

            if G_tw_token=="":
                t_token=tw.send_local_socket("main_widget", "get_token", {}, "get")	
                if isinstance(t_token, bool)!=True and t_token!="":
                    G_tw_token=t_token
                    G_is_login=True

          
    
    def get_version(self): 
        u"""
         描述: 获取tw版本
         调用: get_version()   
         返回: 成功返回str
         """          
        return self.__version__
    
    #发送到web
    @staticmethod
    def send_web(a_controller, a_method, a_data_dict):
        u"""
         描述: post到后台
         调用: send_web(a_controller, a_method, a_data_dict)
               ---> a_controller              控制器 (str/unicode)
               ---> a_method                  方法 (str/unicode)
               ---> a_data_dict               post的数据 (dict)
         返回: 按实际情况
         """          
        global G_tw_http_ip
        global G_tw_token 
        return _con.send(G_cgtw_session, G_tw_http_ip, G_tw_token, a_controller, a_method, a_data_dict)

    @staticmethod
    def send_local_http(a_db, a_module, a_action, a_other_data_dict, a_type="send"):
        u"""
         描述: post到客户端的http server
         调用: send_local_http(a_db, a_module, a_action, a_other_data_dict, a_type="send")
               ---> a_db                      数据库 (str/unicode)
               ---> a_module                  模块 (str/unicode)
               ---> a_action                  动作 (str/unicode)
               ---> a_other_data_dict         post的数据 (dict)
               ---> a_type                    类型 (str/unicode), send/get
               
         返回: 按实际情况
         """          
        return _con_local.send_http(a_module, a_db, a_action, a_other_data_dict, a_type)

    @staticmethod
    def send_local_socket(a_sign, a_method, a_data, a_type="get"):
        u"""
         描述: post到客户端的websocket server
         调用: send_local_socket(a_sign, a_method, a_data, a_type="get")
               ---> a_sign                    标识 (str/unicode)
               ---> a_method                  方法 (str/unicode)
               ---> a_data                    post的数据 (dict)
                ---> a_type                   类型 (str/unicode), send/get
         返回: 按实际情况
         """            
        return _con_local.send_socket(a_sign, a_method, a_data, a_type)

    
    @staticmethod
    def send_msg(a_db, a_module, a_moduel_type, a_task_id, a_account_id_list, a_content=""):
        u"""
         描述: 发送消息到客户端
         调用: send_msg(a_db, a_module, a_moduel_type, a_task_id, a_account_id_list, a_content="")
               ---> a_db                      数据库 (str/unicode)
               ---> a_module                  模块 (str/unicode)
               ---> a_moduel_type             模块类型 (str/unicode)
               ---> a_task_id                 任务ID (str/unicode)
               ---> a_account_id_list         账号ID列表 (list)
               ---> a_content                 发送的内容 (unicode)
         返回: 成功返回True
         """           
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or  not isinstance(a_task_id, (str, unicode)) or not isinstance(a_account_id_list,list) or \
           not isinstance(a_content, (str, unicode)) or  not isinstance(a_moduel_type, (str, unicode)):
            raise Exception("msg.send_messsage argv error ,there must be (str/unicode, str/unicode, str/unicode, str/unicode, list,  str/unicode)")
        return tw.send_web("c_msg","send_task", {"db":a_db, "module":a_module, "task_id":a_task_id, "a_account_id_list":a_account_id_list, "content":a_content, "module_type":a_moduel_type})


    
    class client:

        @staticmethod
        def get_argv_key(a_key):
            u"""
             描述: 获取插件参数
             调用: get_argv_key(a_key)   
                   ---> a_key                 插件配置参数中的键 (str/unicode)
             返回: 成功返回str,失败返回False
             """               
            return _client.get_argv_key(a_key)	

        @staticmethod
        def get_sys_key(a_key):	
            u"""
             描述: 获取系统参数
             调用: get_sys_key(a_key)   
                  ---> a_key                   键 (str/unicode)
             返回: 成功返回str/list, 失败返回Falase
             """              
            return _client.get_sys_key(a_key)
        
        @staticmethod
        def get_database():
            u"""
             描述: 获取当前数据库
             调用: get_database()   
             返回: 成功返回str,失败返回False
             """                
            return _client.get_database()
        
        @staticmethod
        def get_id():
            u"""
             描述: 获取界面选择的id列表
             调用: get_id()   
             返回: 成功返回list,失败返回False
             """               
            return _client.get_id()
        
        @staticmethod
        def get_link_id():
            u"""
             描述: 获取link界面选择的id列表
             调用: get_link_id()   
             返回: 成功返回list,失败返回False
            """               
            return _client.get_link_id()
        
        @staticmethod
        def get_module():
            u"""
             描述: 获取当前模块
             调用: get_module()   
             返回: 成功返回str,失败返回False
             """                 
            return _client.get_module()
        
        @staticmethod
        def get_module_type():
            u"""
             描述: 获取当前模块类型
             调用: get_module_type()   
             返回: 成功返回str,失败返回False
             """              
            return _client.get_module_type()
        
        @staticmethod
        def get_file():
            u"""
             描述: 获取拖入文件框的源文件路径
             调用: get_file()   
             返回: 成功返回list,失败返回False
             """  
            return _client.get_file()
        
        
        @staticmethod
        def get_folder():
            u"""
             描述: 获取拖入文件框,文件所在的目录
             调用: get_folder()   
             返回: 成功返回str,失败返回False
             """               
            return _client.get_folder()
        
        
        @staticmethod
        def send_to_qc_widget(a_db, a_module, a_module_type, a_task_id, a_node_data_dict):
            #发送给qt的界面弹出approve或者retake的界面
            #a_node_data_dict为里面一堆的节点的数据，用于更改流程
            if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or not isinstance(a_task_id, (str, unicode))  or not isinstance(a_node_data_dict, dict):
                raise Exception("client.send_to_qc_widget argv error ,there must be (str/unicode, str/unicode, str/unicode, str/unicode, dict)")
            return tw.send_local_http(a_db, a_module, "send_to_qc_widget",  {"node_data":[a_node_data_dict], "task_id":a_task_id, "module_type":a_module_type})
    
    
    class login:
        
        @staticmethod
        def account():
            u"""
            描述: 获取当前登陆账号
            调用: account()   
            返回: 成功返回str
            """              
            global G_tw_account
            global G_tw_token
            if tw.login.is_login()==False:
                return ""
            t_account=tw.send_web("c_token", "get_account", {"token":G_tw_token})
            return t_account

        @staticmethod
        def account_id():
            u"""
            描述: 获取当前登陆账号的ID
            调用: account_id()   
            返回: 成功返回str
            """                 
            global G_tw_account_id	
            global G_tw_token
            if tw.login.is_login()==False:
                return ""
            return tw.send_web("c_token", "get_account_id", {"token":G_tw_token})

        @staticmethod
        def token():
            u"""
            描述: 获取验证的token
            调用: token()   
            返回: 成功返回str
            """               
            global G_tw_token
            return G_tw_token


        @staticmethod
        def http_server_ip():
            u"""
            描述: 获取server 的IP
            调用: http_server_ip()   
            返回: 成功返回str
            """  
            global G_tw_http_ip
            return G_tw_http_ip
        @staticmethod
        def is_login():
            u"""
            描述: 判断是否登录
            调用: is_login()   
            返回: 返回bool
            """               
            global G_tw_token
            if G_tw_token=="":
                return False
            return True
    
    class status:

        @staticmethod
        def get_status_and_color():
            u"""
            描述: 获取状态的名称和颜色
            调用: get_status_and_color()
            返回: 成功返回dict
            """            
            return tw.send_web("c_status",  "get_status_and_color", {})
        
    class info:
        __module_type="info"
        @staticmethod
        def modules(a_db):
            u"""
            描述: 获取可以调用的信息模块
            调用: modules(a_db)
                  --> a_db                      数据库 (str/unicode)
            返回: 成功返回list
            """             
            return _module.modules(tw.send_web, a_db, tw.info.__module_type)  
                
        @staticmethod
        def get_id(a_db, a_module, a_filter_list, a_limit="5000", a_start_num=""):
            u"""
            描述: 获取ID列表
            调用: get_id(a_db, a_module, a_filter_list, a_limit="5000", a_start_num="")
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_filter_list             过滤语句列表 (list)
                 --> a_limit                   限制条数 (str/unicode), 默认是5000
                 --> a_start_num               开始条数 (str/unicode), 默认为""
            返回: 成功返回list
            """             
            return _module.get_id(tw.send_web, a_db, a_module, tw.info.__module_type, a_filter_list, a_limit="5000", a_start_num="")
                    
        @staticmethod
        def get(a_db, a_module, a_id_list, a_field_sign_list, a_limit="5000", a_order_sign_list=[]):
            u"""
            描述: 取出相对应的字段信息
            调用: get(a_db, a_module, a_id_list, a_field_sign_list, a_limit="5000", a_order_sign_list=[])
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id_list                ID列表 (list)
                 --> a_field_sign_list        字段标识列表 (list)
                 --> a_limit                  限制条数 (str/unicode), 默认是5000
                 --> a_order_sign_list        顺序的字段标识列表 (list)
                 
            返回: 成功返回list
            """                 
            return _module.get(tw.send_web, a_db, a_module, tw.info.__module_type, a_id_list, a_field_sign_list, a_limit, a_order_sign_list)       
            
        @staticmethod
        def get_dir(a_db, a_module, a_id_list, a_folder_sign_list):
            u"""
            描述: 取出相对应的路径列表
            调用: get_dir(a_db, a_module, a_id_list, a_folder_sign_list)
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id_list                ID列表 (list)
                 --> a_folder_sign_list       目录标识列表 (list)

            返回: 成功返回list
            """               
            return _module.get_dir(tw.send_web, a_db, a_module, tw.info.__module_type, a_id_list, a_folder_sign_list)   
        
        @staticmethod
        def get_field_and_dir(a_db, a_module, a_id_list, a_field_sign_list, a_folder_sign_list):
            u"""
            描述: 取出相对应的字段和路径
            调用: get_field_and_dir(a_db, a_module, a_id_list, a_field_sign_list, a_folder_sign_list)
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id_list                ID列表 (list)
                 --> a_field_sign_list        字段标识列表 (list)
                 --> a_folder_sign_list       目录标识列表 (list)

            返回: 成功返回list
            """                
            return _module.get_field_and_dir(tw.send_web, a_db, a_module, tw.info.__module_type, a_id_list, a_field_sign_list, a_folder_sign_list)        
        
        @staticmethod
        def get_makedirs(a_db, a_module, a_id_list):      
            u"""
            描述:获取要创建的目录
            调用:get_makedirs(a_db, a_module, a_id_list)
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id_list                ID列表 (list)
            返回: 成功返回list
             """               
            return _module.get_makedirs(tw.send_web, a_db, a_module, tw.info.__module_type, a_id_list)
        
        @staticmethod
        def get_sign_filebox(a_db, a_module, a_id, a_filebox_sign):    
            u"""
            描述: 根据文件框标识获取文件框信息
            调用: get_sign_filebox(a_db, a_module, a_id, a_filebox_sign)
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id                     ID (str/unicode)
                 --> a_filebox_sign           文件框标识 (str/unicode)
            返回: 成功返回dict
            """                 
            return _module.get_sign_filebox(tw.send_web, a_db, a_module, tw.info.__module_type, a_id, a_filebox_sign)
        
        @staticmethod
        def get_filebox(a_db, a_module, a_id, a_filebox_id):    
            u"""
            描述: 根据文件框ID获取文件框信息
            调用: get_filebox(a_db, a_module, a_id, a_filebox_id)
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id                     ID (str/unicode)
                 --> a_filebox_id             文件框ID (str/unicode)
            返回: 成功返回dict
            """                
            return _module.get_filebox(tw.send_web, a_db, a_module, tw.info.__module_type, a_id, a_filebox_id)  

        @staticmethod
        def set(a_db, a_module, a_id_list, a_sign_data_dict):
            u"""
            描述: 修改数据
            调用: set(a_db, a_module, a_id_list, a_sign_data_dict)
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id_list                ID列表 (list)
                 --> a_sign_data_dict         更新的数据(dict), 格式:{"字段标识" : "值", "字段标识" : "值" }
            返回: 成功返回True
            """                
            return _module.set(tw.send_web, a_db, a_module, tw.info.__module_type, a_id_list, a_sign_data_dict)

        @staticmethod
        def delete(a_db, a_module, a_id_list):
            u"""
            描述: 删除数据
            调用: delete(a_db, a_module, a_id_list)
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id_list                ID列表 (list)
            返回: 成功返回True
            """               
            return _module.delete(tw.send_web, a_db, a_module, tw.info.__module_type, a_id_list)
        
        @staticmethod
        def create(a_db, a_module, a_sign_data_dict, a_is_return_id=False):
            u"""
            描述: 创建数据
            调用: create(a_db, a_module, a_sign_data_dict)
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_sign_data_dict         创建的数据 (dict), 格式:{字段标识1: 值1, 字段标识2: 值2, 字段标识3:值3}
                 --> a_is_return_id           是否返回创建的ID （bool）,  a_is_return_id=True,返回的是创建的ID
            返回: 成功返回True/str
            """              
            return _module.create(tw.send_web, a_db, a_module, tw.info.__module_type, a_sign_data_dict, a_is_return_id)

        @staticmethod
        def download_image(a_db, a_module, a_id_list, a_field_sign, a_is_small=True, a_local_path=""):
            u"""
            描述: 下载图片
            调用: download_image(a_db, a_module, a_id_list, a_field_sign, a_is_small=True, a_local_path="")
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id_list                ID列表 (list)
                 --> a_field_sign             图片字段标识 (str/unicode)
                 --> a_is_small               是否下载小图 (bool), 默认为True
                 --> a_local_path             指定路径 (unicode), 默认为temp路径
            返回: 成功返回list
            """                
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            return _module.download_image(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, a_db, a_module, tw.info.__module_type, a_id_list, a_field_sign, a_is_small, a_local_path)
        
        @staticmethod
        def set_image(a_db, a_module, a_id_list, a_field_sign, a_img_path, a_compress="1080"):
            u"""
             描述: 修改图片字段的图片
             调用: set_image(a_db, a_module, a_id_list, a_field_sign, a_img_path, a_compress="1080")
                  --> a_db                    数据库 (str/unicode)
                  --> a_module                模块 (str/unicode)
                  --> a_id_list               ID列表 (list)
                  --> a_field_sign            图片字段标识 (str/unicode)
                  --> a_img_path              图片路径 (unicode)
                  --> a_compress              压缩比例 (str/unicode), 可选值 no_compress(无压), 1080(1920x1080), 720(1280x720), 540(960x540)
             返回: 成功返回True
             """                 
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            return _module.set_image(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, a_db, a_module, tw.info.__module_type, a_id_list, a_field_sign, a_img_path, a_compress)

        @staticmethod
        def count(a_db, a_module, a_filter_list):
            u"""
             描述: 计算数量
             调用: count(a_db, a_module, a_filter_list)
                  --> a_db                    数据库 (str/unicode)
                  --> a_module                模块 (str/unicode)
                  --> a_filter_list           过滤语句列表 (list)
             返回: 成功返回str
             """              
            return _module.count(tw.send_web, a_db, a_module, tw.info.__module_type, a_filter_list)
        
        @staticmethod
        def distinct(a_db, a_module, a_filter_list, a_field_sign, a_order_sign_list=[]):
            u"""
             描述: 取某列字段消除重复后的结果
             调用: distinct(a_db, a_module, a_filter_list, a_field_sign, a_order_sign_list=[])
                  --> a_db                    数据库 (str/unicode)
                  --> a_module                模块 (str/unicode)
                  --> a_filter_list           过滤语句列表 (list)
                  --> a_field_sign            字段标识 (str/unicode)
                  --> a_order_sign_list       排序列表 (list)
             返回: 成功返回list
             """                
            return _module.distinct(tw.send_web, a_db, a_module, tw.info.__module_type, a_filter_list, a_field_sign, a_order_sign_list)

        
    
    class task:
        __module_type="task"
        @staticmethod
        def modules(a_db):
            u"""
            描述: 获取可以调用的制作模块
            调用: modules(a_db)
                  --> a_db                    数据库 (str/unicode)
            返回: 成功返回list
            """              
            return _module.modules(tw.send_web, a_db, tw.task.__module_type)          
            
        @staticmethod
        def get_id(a_db, a_module, a_filter_list, a_limit="5000", a_start_num=""):
            u"""
            描述: 获取ID列表
            调用: get_id(a_db, a_module, a_filter_list, a_limit="5000", a_start_num="")
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_filter_list            过滤语句列表 (list)
                 --> a_limit                  限制条数 (list), 默认是5000
                 --> a_start_num              起始条数 (str/unicode), 默认为""
            返回: 成功返回list
            """                  
            return _module.get_id(tw.send_web, a_db, a_module, tw.task.__module_type, a_filter_list, a_limit="5000", a_start_num="")
                    
        @staticmethod
        def get(a_db, a_module, a_id_list, a_field_sign_list, a_limit="5000", a_order_sign_list=[]):
            u"""
            描述: 取出相对应的字段信息
            调用: get(a_db, a_module, a_id_list, a_field_sign_list, a_limit="5000", a_order_sign_list=[])
                 --> a_db                     数据库 (str/unicode)
                 --> a_module                 模块 (str/unicode)
                 --> a_id_list                ID列表 (list)
                 --> a_field_sign_list        字段标识列表 (list)
                 --> a_limit                  限制条数 (str/unicode), 默认是5000
                 --> a_order_sign_list        排序的字段标识列表 (list)
            返回: 成功返回list
            """                 
            return _module.get(tw.send_web, a_db, a_module, tw.task.__module_type, a_id_list, a_field_sign_list, a_limit, a_order_sign_list)       
            
        @staticmethod
        def get_dir(a_db, a_module, a_id_list, a_folder_sign_list):
            u"""
            描述: 取出相对应的路径列表
            调用: get_dir(a_db, a_module, a_id_list, a_folder_sign_list)
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_id_list                 ID列表 (list)
                 --> a_folder_sign_list        目录标识列表 (list)

            返回: 成功返回list
            """               
            return _module.get_dir(tw.send_web, a_db, a_module, tw.task.__module_type, a_id_list, a_folder_sign_list)   
        
        @staticmethod
        def get_field_and_dir(a_db, a_module, a_id_list, a_field_sign_list, a_folder_sign_list):
            u"""
            描述: 取出相对应的字段和路径
            调用: get_field_and_dir(a_db, a_module, a_id_list, a_field_sign_list, a_folder_sign_list)
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_id_list                 ID列表 (list)
                 --> a_field_sign_list         字段标识列表 (list)
                 --> a_folder_sign_list        目录标识列表 (list)

            返回: 成功返回list
            """                      
            return _module.get_field_and_dir(tw.send_web, a_db, a_module, tw.task.__module_type, a_id_list, a_field_sign_list, a_folder_sign_list)        
                
        @staticmethod
        def get_makedirs(a_db, a_module, a_id_list):   
            u"""
            描述:获取要创建的目录
            调用:get_makedirs(a_db, a_module, a_id_list)
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_id_list                 ID列表 (list)
            返回: 成功返回list
             """             
            return _module.get_makedirs(tw.send_web, a_db, a_module, tw.task.__module_type, a_id_list)
        
        @staticmethod
        def get_submit_filebox(a_db, a_module, a_id):
            u"""
            描述: 获取提交文件框信息
            调用: get_submit_filebox(a_db, a_module, a_id)
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_id                      ID (str/unicode)
            返回: 成功返回dict
            """                
            return _module.get_submit_filebox(tw.send_web, a_db, a_module, tw.task.__module_type, a_id)

        @staticmethod
        def get_sign_filebox(a_db, a_module, a_id, a_filebox_sign):   
            u"""
            描述: 根据文件框标识获取文件框信息
            调用: get_sign_filebox(a_db, a_module, a_id, a_filebox_sign)
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_id                      ID (str/unicode)
                 --> a_filebox_sign            文件框标识 (str/unicode)
            返回: 成功返回dict
            """                  
            return _module.get_sign_filebox(tw.send_web, a_db, a_module, tw.task.__module_type, a_id, a_filebox_sign)
        
        @staticmethod
        def get_filebox(a_db, a_module, a_id, a_filebox_id):    
            u"""
            描述: 根据文件框ID获取文件框信息
            调用: get_filebox(a_db, a_module, a_id, a_filebox_id)
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_id                      ID (str/unicode)
                 --> a_filebox_id              文件框ID (str/unicode)
            返回: 成功返回dict
            """                
            return _module.get_filebox(tw.send_web, a_db, a_module, tw.task.__module_type, a_id, a_filebox_id)        
        
        @staticmethod
        def set(a_db, a_module, a_id_list, a_sign_data_dict):
            u"""
            描述: 修改数据
            调用: set(a_db, a_module, a_id_list, a_sign_data_dict)
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_id_list                 ID (str/unicode)
                 --> a_sign_data_dict          更新数据 (dict), 格式:{"字段标识" : "值", "字段标识" : "值" }
            返回: 成功返回True
            """            
            return _module.set(tw.send_web, a_db, a_module, tw.task.__module_type, a_id_list, a_sign_data_dict)

        @staticmethod
        def delete(a_db, a_module, a_id_list):
            u"""
            描述: 删除数据
            调用: delete(a_db, a_module, a_id_list)
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_id_list                 ID列表 (list)
            返回: 成功返回True
            """             
            return _module.delete(tw.send_web, a_db, a_module, tw.task.__module_type, a_id_list)
        
        @staticmethod
        def create(a_db, a_module, a_join_id, a_pipeline_id, a_task_name, a_flow_id):
            u"""
            描述: 创建
            调用: create(a_db, a_module, a_join_id, a_pipeline_id, a_task_name, a_flow_id)
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_join_id                 信息表的ID (str/unicode)
                 --> a_pipeline_id             阶段ID (str/unicode)
                 --> a_task_name               任务名称 (str/unicode)
                 --> a_flow_id                 流程ID (str/unicode)
            返回: 成功返回list
            """            
            return _module.create_task(tw.send_web, a_db, a_module, tw.task.__module_type, a_join_id, a_pipeline_id, a_task_name, a_flow_id) 

        @staticmethod
        def download_image(a_db, a_module, a_id_list, a_field_sign, a_is_small=True, a_local_path=""):
            u"""
            描述: 下载图片
            调用: download_image(a_db, a_module, a_id_list, a_field_sign, a_is_small=True, a_local_path="")
                 --> a_db                      数据库 (str/unicode)
                 --> a_module                  模块 (str/unicode)
                 --> a_id_list                 ID列表 (list)
                 --> a_field_sign              图片字段标识 (str/unicode)
                 --> a_is_small                是否下载小图 (bool), 默认为True
                 --> a_local_path              指定路径 (str/unicode), 默认为temp路径
            返回: 成功返回list
            """             
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            return _module.download_image(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, a_db, a_module, tw.task.__module_type, a_id_list, a_field_sign, a_is_small, a_local_path)
        
        @staticmethod
        def set_image(a_db, a_module, a_id_list, a_field_sign, a_img_path, a_compress="1080"):
            u"""
             描述: 修改图片字段的图片
             调用: set_image(a_db, a_module, a_id_list, a_field_sign, a_img_path, a_compress="1080")
                  --> a_db                     数据库 (str/unicode)
                  --> a_module                 模块 (str/unicode)
                  --> a_id_list                ID列表 (list)
                  --> a_field_sign             图片字段标识 (str/unicode)
                  --> a_img_path               图片路径 (unicode)
                  --> a_compress               压缩比例 (str/unicode), 可选值 no_compress(无压), 1080(1920x1080), 720(1280x720), 540(960x540)
             返回: 成功返回True
             """                
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token
            return _module.set_image(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, a_db, a_module, tw.task.__module_type, a_id_list, a_field_sign, a_img_path, a_compress)

        @staticmethod
        def count(a_db, a_module, a_filter_list):
            u"""
             描述: 计算数量
             调用: count(a_db, a_module, a_filter_list)
                  --> a_db                     数据库 (str/unicode)
                  --> a_module                 模块 (str/unicode)
                  --> a_filter_list            过滤语句列表 (list)
             返回: 成功返回str
             """                
            return _module.count(tw.send_web, a_db, a_module, tw.task.__module_type, a_filter_list)
        
        @staticmethod
        def distinct(a_db, a_module, a_filter_list, a_field_sign, a_order_sign_list=[]):
            u"""
             描述: 取某列字段消除重复后的结果
             调用: distinct(a_db, a_module, a_filter_list, a_field_sign, a_order_sign_list=[])
                  --> a_db                     数据库 (str/unicode)
                  --> a_module                 模块 (str/unicode)
                  --> a_filter_list            过滤语句列表 (list)
                  --> a_field_sign             字段标识 (str/unicode)
                  --> a_order_sign_list        排序列表 (list)
             返回: 成功返回list
             """               
            return _module.distinct(tw.send_web, a_db, a_module, tw.task.__module_type, a_filter_list, a_field_sign, a_order_sign_list)

        

        @staticmethod
        def assign(a_db, a_module,  a_id_list, a_assign_account_id, a_start_date="", a_end_date=""):
            u"""
             描述: 分配制作人员
             调用: assign(a_db, a_module,  a_id_list, a_assign_account_id, a_start_date="", a_end_date="")
                  --> a_db                      数据库 (str/unicode)
                  --> a_module                  模块 (str/unicode)
                  --> a_id_list                 ID列表 (list)
                  --> a_assign_account_id       制作者ID (str/unicode)
                  --> a_start_date              预计开始日期 (str/unicode), 格式:2018-01-01, 默认为""
                  --> a_end_date                预计完成日期 (str/unicode), 格式:2018-01-01, 默认为""
             返回: 成功返回True
             """               
            return _module.assign(tw.send_web, a_db, a_module, tw.task.__module_type, a_id_list, a_assign_account_id, a_start_date, a_end_date)
        
        @staticmethod
        def submit(a_db, a_module, a_id, a_file_path_list, a_note="",a_path_list=[]):
            u"""
             描述: 提交审核文件
             调用: submit(a_db, a_module, a_id, a_file_path_list, a_note="",a_path_list=[])
                  --> a_db                      数据库 (str/unicode)
                  --> a_module                  模块 (str/unicode)
                  --> a_id                      id (str/unicode)
                  --> a_file_path_list          文件完整路径列表 (list); 如拖入bb文件夹, 则为[z:/aa/bb/test001.0001.png, z:/aa/bb/test001.0002.png]
                  --> a_note                    内容 (str/unicode), 默认为""
                  --> a_path_list               文件路径列表 (list), 默认为[]; 如拖入bb文件夹,[z:/aa/bb], 如果提交的文件,两个是一样的。如果提交的是文件夹。这边记录到文件夹的名称
             返回: 成功返回True
             """               
            t_account_id=tw.login.account_id()
            return _module.submit(tw.send_web, t_account_id, a_db, a_module, tw.task.__module_type, a_id, a_file_path_list, a_note,a_path_list)
        
        @staticmethod
        def update_flow(a_db, a_module, a_id, a_field_sign, a_status, a_note=""):
            u"""
             描述: 更改某环节状态
             调用: update_flow(a_db, a_module, a_id, a_field_sign, a_status, a_note="")
                  --> a_db                      数据库 (str/unicode)
                  --> a_module                  模块 (str/unicode)
                  --> a_id                      id (str/unicode)
                  --> a_field_sign              字段标识 (str/unicode)
                  --> a_status                  状态 (str/unicode)
                  --> a_note                    内容 (str/unicode), 默认为""
             返回: 成功返回True
             """               
            return _module.update_flow(tw.send_web, a_db, a_module, tw.task.__module_type, a_id, a_field_sign, a_status, a_note)
        


    class note:  
        @staticmethod
        def fields():
            u"""
             描述:获取note字段
             调用:fields()
             返回:成功返回list
             """                
            from twlib._note import _note
            return _note.fields()
        
        @staticmethod
        def get_id(a_db, a_filter_list, a_limit="5000"):
            u"""
             描述:获取note ID列表
             调用:get_id(a_db, a_filter_list, a_limit="5000")
                  --> a_db                      数据库 (str/unicode)
                  --> a_filter_list             过滤语句列表 (list)
                  --> a_limit                   限制条数 (str/unicode), 默认是5000
             返回: 成功返回list
             """   
            from twlib._note import _note
            return _note.get_id(tw.send_web, a_db, a_filter_list, a_limit)
        
        @staticmethod
        def get(a_db, a_id_list, a_field_list, a_limit="5000", a_order_list=[]):
            u"""
             描述:获取note信息
             调用:get(a_db, a_id_list, a_field_list, a_limit="5000", a_order_list=[])
                  --> a_db                      数据库 (str/unicode)
                  --> a_id_list                 ID列表 (list)
                  --> a_field_list              字段列表 (list)
                  --> a_limit                   限制条数 (str/unicode), 默认是5000
                  --> a_order_list              排序列表 (list)
             返回: 成功返回list
             """                
            from twlib._note import _note
            return _note.get(tw.send_web, a_db, a_id_list, a_field_list, a_limit, a_order_list)
        
        @staticmethod
        def create(a_db, a_module, a_module_type, a_task_id_list, a_text, a_cc_acount_id="", a_image_list=[]):
            u"""
             描述:创建
             调用:create(a_db, a_module, a_module_type, a_task_id_list, a_text, a_cc_acount_id="", a_image_list=[])
                  --> a_db                      数据库 (str/unicode)
                  --> a_module                  模块 (str/unicode)
                  --> a_module_type             模块类型 (str/unicode)
                  --> a_task_id_list            任务的ID列表 (list)
                  --> a_text                    内容 (str/unicode)
                  --> a_cc_acount_id            抄送账号ID (str/unicode), 默认为""
                  --> a_image_list              图片路径列表 (list), 默认为[]
             返回:成功返回True
             """                
            from twlib._note import _note
            global G_tw_http_ip
            global G_cgtw_path
            global G_tw_token       
            t_account_id = tw.login.account_id()
            return _note.create(tw.send_web, G_tw_http_ip, G_cgtw_path, G_tw_token, t_account_id, a_db, a_module, a_module_type, a_task_id_list, a_text, a_cc_acount_id, a_image_list)
        

    class filebox:
        @staticmethod
        def fields():
            u"""
             描述:获取文件框字段
             调用:fields()
             返回:成功返回list
             """               
            from twlib._filebox import _filebox
            return _filebox.fields()    
        
        @staticmethod
        def get_id(a_db, a_filter_list):
            u"""
             描述:获取文件框ID列表
             调用:get_id(a_db, a_filter_list)
                  --> a_db                      数据库 (str/unicode)
                  --> a_filter_list             过滤语句列表 (list)
             返回:成功返回list
             """               
            from twlib._filebox import _filebox
            return _filebox.get_id(tw.send_web, a_db, a_filter_list)
                    
        @staticmethod
        def get(a_db, a_id_list, a_field_list):
            u"""
             描述:获取文件框信息
             调用:get(a_db, a_id_list, a_field_list)
                  --> a_id_list                 文件框ID列表 (list)
                  --> a_field_list              字段列表 (list)
             返回:成功返回list
             """             
            from twlib._filebox import _filebox
            return _filebox.get(tw.send_web, a_db, a_id_list, a_field_list)
        

    
    class field:
        @staticmethod
        def type():
            u"""
             描述:获取字段类型
             调用:type()
             返回:成功返回list
             """               
            from twlib._field import _field
            return _field.type()
        
        @staticmethod
        def create(a_db, a_module, a_module_type, a_chinese_name, a_english_name, a_sign, a_type, a_field_name=""):
            u"""
             描述:创建字段
             调用:create(a_db, a_module, a_module_type, a_chinese_name, a_english_name, a_sign, a_type, a_field_name="")
                  --> a_db                      数据库 (str/unicode)
                  --> a_module                  模块 (str/unicode)
                  --> a_module_type             模块类型 (str/unicode)
                  --> a_chinese_name            中文名 (str/unicode)
                  --> a_english_name            英文名 (str/unicode)
                  --> a_sign                    字段标识 (str/unicode)
                  --> a_type                    类型 (str/unicode)
                  --> a_field_name              字段名 (str/unicode), 默认为"",为空时,默认和sign一样
             返回:成功返回True
             """              
            from twlib._field import _field
            return _field.create(tw.send_web, a_db, a_module, a_module_type, a_chinese_name, a_english_name, a_sign, a_type, a_field_name)
        

        
    class plugin:
        
        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """                
            from twlib._plugin import _plugin
            return _plugin.fields()
        
        @staticmethod
        def get_id(a_filter_list):
            u"""
             描述:获取插件ID
             调用:get_id（a_filter_list）
                  --> a_filter_list            过滤语句列表 (list)
             返回:成功返回list
             """                  
            from twlib._plugin import _plugin 
            return _plugin.get_id(tw.send_web, a_filter_list)
                    
        @staticmethod
        def get(a_id_list, a_field_list):
            u"""
             描述:获取插件信息
             调用:get(a_id_list, a_field_list)
                  --> a_id_list                ID列表 (list)
                  --> a_field_list             字段列表 (list)
             返回:成功返回list
             """                 
            from twlib._plugin import _plugin 
            return _plugin.get(tw.send_web, a_id_list, a_field_list)
        
        @staticmethod
        def get_argvs(a_id):    
            u"""
             描述:获取插件配置参数
             调用:get_argvs(a_id):  
                  --> a_id                    插件ID (str/unicode)
             返回:成功返回dict
             """               
            from twlib._plugin import _plugin 
            return _plugin.get_argvs(tw.send_web, a_id)
        
        @staticmethod
        def set_argvs(a_id, a_argvs_dict):  
            u"""
             描述:设置插件参数
             调用:set_argvs(a_id, a_argvs_dict):  
                  --> a_id                    插件ID (str/unicode)
                  --> a_argvs_dict            更新参数 (dict), 格式{'key':'value'}
             返回:成功返回True
             """              
            from twlib._plugin import _plugin 
            return _plugin.set_argvs(tw.send_web, a_id, a_argvs_dict)
        



    class pipeline:
        
        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """   
            from twlib._pipeline import _pipeline
            return _pipeline.fields()
        
        @staticmethod
        def get_id(a_db, a_filter_list):
            u"""
             描述:获得阶段ID
             调用:get_id(a_db, a_filter_list)
                  --> a_db                    数据库 (str/unicode)
                  --> a_filter_list           过滤语句列表 (list)
             返回:成功返回list
             """              
            from twlib._pipeline import _pipeline
            return _pipeline.get_id(tw.send_web, a_db, a_filter_list)
                    
        @staticmethod
        def get(a_db, a_id_list, a_field_list):
            u"""
             描述:获取阶段信息
             调用:get(a_db, a_id_list, a_field_list)
                  --> a_db                   数据库 (str/unicode)
                  --> a_id_list              ID列表 (list)
                  --> a_field_list           字段列表 (list)
             返回:成功返回list
             """             
            from twlib._pipeline import _pipeline
            return _pipeline.get(tw.send_web, a_db, a_id_list, a_field_list)
        


    class history:

        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """   
            from twlib._history import _history
            return _history.fields() 
        
        @staticmethod
        def get_id(a_db, a_filter_list, a_limit="5000"):
            u"""
             描述:获取历史id列表
             调用:get_id(a_db, a_filter_list, a_limit="5000")
                 --> a_db                    数据库 (str/unicode)
                 ---a_filter_list            过滤语句列表 (list)
                 --> a_limit                 限制条数 (str/unicode), 默认是5000
             返回:成功返回list
             """              
            from twlib._history import _history
            return _history.get_id(tw.send_web, a_db, a_filter_list, a_limit)
                    
        @staticmethod
        def get(a_db, a_id_list, a_field_list, a_limit="5000", a_order_list=[]):
            u"""
             描述:获取信息
             调用:get(a_db, a_id_list, a_field_list, a_limit="5000", a_order_list=[])
                 --> a_db                    数据库 (str/unicode)
                 --> a_id_list               id列表 (list)
                 --> a_field_list            字段列表 (list)
                 --> a_limit                 限制条数 (str/unicode), 默认是5000
                 --> a_order_list            排序列表 (list), 默认为[]
             返回: 成功返回list
             """                 
            from twlib._history import _history
            return _history.get(tw.send_web, a_db, a_id_list, a_field_list, a_limit, a_order_list)   

        @staticmethod
        def count(a_db, a_filter_list):
            u"""
             描述:获取数量
             调用:count(a_db, a_filter_list)
                  --> a_db                   数据库 (str/unicode)
                  --> a_filter_list          过滤语句列表 (list)
             返回:成功返回str
             """               
            from twlib._history import _history
            return _history.count(tw.send_web, a_db, a_filter_list) 
    

        

    class link:
        @staticmethod
        def link_asset(a_db, a_module, a_module_type, a_id_list, a_link_id_list):
            u"""
             描述:关联资产
             调用:link_asset(a_db, a_module, a_module_type, a_id_list, a_link_id_list)
                 --> a_db                   数据库 (str/unicode)
                 --> a_module               模块 (str/unicode)
                 --> a_module_type          模块类型 (str/unicode)
                 --> a_id_list              任务ID列表 (list)
                 --> a_link_id_list         资产ID列表 (list)
             返回:成功返回True
             """             
            from twlib._link import _link
            return _link.link_asset(tw.send_web, a_db, a_module, a_module_type, a_id_list, a_link_id_list)

        @staticmethod
        def unlink_asset(a_db, a_module, a_module_type, a_id_list, a_link_id_list):
            u"""
             描述:取消关联资产
             调用:unlink_asset(a_db, a_module, a_module_type, a_id_list, a_link_id_list)
                 --> a_db                  数据库 (str/unicode)
                 --> a_module              模块 (str/unicode)
                 --> a_module_type         模块类型 (str/unicode)
                 --> a_id_list             任务ID列表 (list)
                 --> a_link_id_list        资产ID列表 (list)
             返回:成功返回True
             """              
            from twlib._link import _link
            return _link.unlink_asset(tw.send_web, a_db, a_module, a_module_type, a_id_list, a_link_id_list)

        @staticmethod
        def get_asset(a_db, a_module, a_module_type, a_id):
            u"""
             描述:获取关联资产ID
             调用:get_asset(a_db, a_module, a_module_type, a_id)
                 --> a_db                 数据库 (str/unicode)
                 --> a_module             模块 (str/unicode)
                 --> a_module_type        模块类型 (str/unicode)
                 --> a_id                 任务ID (str/unicode)
             返回:成功返回list
             """               
            from twlib._link import _link
            return _link.get_asset(tw.send_web, a_db, a_module, a_module_type, a_id)

    class software:

        @staticmethod
        def types():
            u"""
             描述:获取软件类型
             调用:types()
             返回:成功返回list
             """               
            from twlib._software import _software
            return _software.types(tw.send_web)
        
        @staticmethod
        def get_path(a_db, a_name):
            u"""
             描述:获取软件路径
             调用:get_path(a_db, a_name):
                  --> a_db                数据库 (str/unicode)
                  --> a_name              软件名称 (str/unicode)
             返回:成功返回str
             """                
            from twlib._software import _software
            return _software.get_path(tw.send_web, a_db, a_name)
            
        @staticmethod
        def get_with_type(a_db, a_type):
            u"""
             描述: 根据类型获取软件信息
             调用: get_with_type(a_db, a_type):
                  --> a_db                数据库 (str/unicode)
                  --> a_type              软件类型 (str/unicode)
             返回: 成功返回list
             """               
            from twlib._software import _software
            return _software.get_with_type(tw.send_web, a_db, a_type)
    

    
    
    class api_data:

        @staticmethod
        def get(a_db, a_key, a_is_user=True):
            u"""
             描述:获取python存储信息
             调用:get(a_db, a_key, a_is_user=True)
                  --> a_db                数据库 (str/unicode)
                  --> a_key               键 (str/unicode)
                  --> a_is_user           是否为个人 (bool), 默认为True
                  
             返回:成功返回str
             """             
            from twlib._api_data import _api_data
            return _api_data.get(tw.send_web, a_db, a_key, a_is_user)
        
        @staticmethod
        def set(a_db, a_key, a_value, a_is_user=True):
            u"""
             描述:设置python存储信息
             调用:set(a_db, a_key, a_value, a_is_user=True)
                  --> a_db                数据库 (str/unicode)
                  --> a_key               键 (str/unicode)
                  --> a_value             值 (str/unicode)
                  --> a_is_user           是否为个人 (bool), 默认为True
                  
             返回:成功返回True
             """                 
            from twlib._api_data import _api_data
            return _api_data.set(tw.send_web, a_db, a_key, a_value, a_is_user)
        




    class version:
        
        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """               
            from twlib._version import _version
            return _version.fields()
        
        @staticmethod
        def get_id(a_db, a_filter_list, a_limit="5000"):
            u"""
             描述:获取版本ID列表
             调用:get_id(a_db, a_filter_list, a_limit="5000")
                  --> a_db                数据库 (str/unicode)
                  --> a_filter_list       过滤列表 (list)
                  --> a_limit             限制条数 (str/unicode), 默认是5000
             返回:成功返回list
             """                
            from twlib._version import _version
            return _version.get_id(tw.send_web, a_db, a_filter_list, a_limit) 
        
        @staticmethod
        def get(a_db, a_id_list, a_field_list, a_limit="5000"):
            u"""
             描述:获取版本信息
             调用:get(a_db, a_id_list, a_field_list, a_limit="5000")
                  --> a_db                数据库 (str/unicode)
                  --> a_id_list           ID列表 (list)
                  --> a_field_list        字段列表 (list)
                  --> a_limit             限制条数 (str/unicode), 默认是5000
             返回:成功返回list
             """               
            from twlib._version import _version
            return _version.get(tw.send_web, a_db, a_id_list, a_field_list, a_limit) 
        
    
        @staticmethod
        def create(a_db, a_link_id,  a_version, a_local_path_list=[], a_web_path_list=[], a_sign="", a_image_list=[], a_from_version=""):
            u"""
             描述:创建版本
             调用:create(a_db, a_link_id,  a_version, a_local_path_list=[], a_web_path_list=[], a_sign="", a_image_list=[], a_from_version="")
                  --> a_db                数据库 (str/unicode)
                  --> a_link_id           关联的任务ID (str/unicode)
                  --> a_version           版本 (str/unicode)
                  --> a_local_path_list   本地路径列表 (list), 默认为[]
                  --> a_web_path_list     web路径列表 (list), 默认为[]
                  --> a_sign              标识 (str/unicode),默认为""
                  --> a_image_list        图片列表 (list),默认为""
                  --> a_from_version      从版本更改 (str/unicode), 默认为""
             返回:成功返回True
             """             
            from twlib._version import _version
            return _version.create(tw.send_web, a_db, a_link_id, a_version,  a_local_path_list, a_web_path_list, a_sign, a_image_list, a_from_version)


        
    class link_entity:
        
        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """                
            from twlib._link_entity import _link_entity
            return _link_entity.fields()
        
        @staticmethod
        def get_name(a_db, a_link_id):
            u"""
             描述:获取关联实体名称
             调用:get_name(a_db, a_link_id)
                  --> a_db                数据库 (str/unicode)
                  --> a_link_id           关联任务的ID (str/unicode)
             返回:成功返回str
             """ 
            from twlib._link_entity import _link_entity
            return _link_entity.get_name(tw.send_web, a_db, a_link_id)
        
        @staticmethod
        def get(a_db, a_filter_list=[]):
            u"""
             描述:获取关联实体名称列表
             调用:get(a_db, a_filter_list=[])
                  --> a_db                数据库 (str/unicode)
                  --> a_filter_list       过滤语句列表 (list)
             返回:成功返回list
             """              
            from twlib._link_entity import _link_entity
            return _link_entity.get(tw.send_web, a_db, a_filter_list)
        

        
    class timelog:
        
        @staticmethod
        def fields():
            u"""
             描述:获取字段
             调用:fields()
             返回:成功返回list
             """               
            from twlib._timelog import _timelog
            return _timelog.fields()  
        
        @staticmethod
        def get_id(a_db, a_filter_list, a_limit="5000"):
            u"""
             描述:获取版本ID列表
             调用:get_id(a_db, a_filter_list, a_limit="5000")
                  --> a_db               数据库 (str/unicode)
                  --> a_filter_list      过滤语句 (list)
                  --> a_limit            限制条数 (str/unicode), 默认是5000
             返回:成功返回list
             """                
            from twlib._timelog import _timelog
            return _timelog.get_id(tw.send_web, a_db, a_filter_list, a_limit) 
        
        @staticmethod
        def get(a_db, a_id_list, a_field_list, a_limit="5000", a_order_list=[]):
            u"""
             描述:获取版本信息
             调用:get(a_db, a_id_list, a_field_list, a_limit="5000", a_order_list=[])
                  --> a_db               数据库 (str/unicode)
                  --> a_id_list          ID列表  (list)
                  --> a_field_list       字段列表 (list)
                  --> a_limit            限制条数 (str/unicode), 默认是5000
                  --> a_order_list       排序列表 (list),默认为空
             返回:成功返回list
             """               
            from twlib._timelog import _timelog
            return _timelog.get(tw.send_web, a_db, a_id_list, a_field_list, a_limit, a_order_list) 
        
    
        @staticmethod
        def create(a_db, a_task_id, a_module, a_module_type, a_use_time, a_date, a_text):
            u"""
             描述:创建
             调用:create(a_db, a_task_id, a_module, a_module_type, a_use_time, a_date, a_text)
                  --> a_db                数据库 (str/unicode)
                  --> a_task_id           关联的任务ID (str/unicode)
                  --> a_module            模块 (str/unicode)
                  --> a_module_type       模块类型 (str/unicode)
                  --> a_use_time          用时 (str/unicode)
                  --> a_date              日期 (str/unicode)
                  --> a_text              内容 (unicode)
             返回:成功返回True
             """             
            from twlib._timelog import _timelog
            return _timelog.create(tw.send_web, a_db, a_task_id, a_module, a_module_type, a_use_time, a_date, a_text)

        @staticmethod
        def set_one(a_db, a_id, a_data_dict):        
            u"""
             描述:更新单个
             调用:set_one(a_db, a_id, a_data_dict)
                  --> a_db                数据库 (str/unicode)
                  --> a_id                ID (str/unicode)
                  --> a_data_dict         更新的数据 (dict)
             返回:成功返回True
             """             
            from twlib._timelog import _timelog
            return _timelog.set_one(tw.send_web, a_db, a_id, a_data_dict)
      
if __name__ == "__main__":
    #
    t_tw = tw("192.168.199.88", "admin", "shiming")
    #print t_tw.get_version()
    
    #---------------client-----------------
    #系统执行插件的读取的
    
    #---------------login-----------------
    #print t_tw.login.account()
    #print t_tw.login.account_id()
    #print t_tw.login.token()
    #print t_tw.login.http_server_ip()
    #print t_tw.login.is_login()
    
    
    #---------------status-----------------
    #print tw.status.get_status_and_color()
    
    
    #---------------info-----------------
    #print t_tw.info.modules("proj_big")
    #t_id_list=t_tw.info.get_id("proj_big", "shot", [ ["eps.eps_name", "=", "EP01"],["shot.shot", "=", "shot110"]])
    #print t_id_list
    #print t_tw.info.get("proj_big", "shot", t_id_list,  ["eps.eps_name", "shot.shot"])
    #print t_tw.info.get_dir("proj_big", "shot", t_id_list,  ["layout_work", "layout_approve"])
    #print t_tw.info.get_field_and_dir("proj_big", "shot",  t_id_list,  ["eps.eps_name", "shot.shot"], ["layout_work", "layout_approve"])
    #print t_tw.info.get_makedirs("proj_big", "shot", t_id_list)
    #print t_tw.info.get_sign_filebox("proj_big", "shot", t_id_list[0], "test_filebox_sign")
    #print t_tw.info.get_filebox("proj_big", "shot", t_id_list[0], u"2118B732-3D78-51F5-48CB-854AFC2C198F")
    #print t_tw.info.set("proj_big", "shot",  t_id_list,  {"shot.frame":"33"})
    #print t_tw.info.delete("proj_big", "shot", t_id_list)
    #print t_tw.info.create("proj_big", "shot", {"shot.shot":"c99", "eps.eps_name":"EP05"})
    #print t_tw.info.download_image("proj_big", "shot", t_id_list, "shot.image")
    #print t_tw.info.set_image("proj_big", "shot", t_id_list, "shot.image", u"z:/png/test001.png")
    #print t_tw.info.count("proj_big", "shot", [  ["eps.eps_name", "=", "EP01"] ])
    #print t_tw.info.distinct("proj_big", "shot", [], "eps.eps_name", ["eps.eps_name"])
    
    
    #---------------task-----------------
    #print t_tw.task.modules("proj_big")
    #t_id_list=t_tw.task.get_id("proj_big", "shot", [ ["eps.eps_name", "=", "EP01"],["shot.shot", "=", "shot001"], ["task.task_name", "=", "Layout"]])
    #print t_id_list
    #print t_tw.task.get("proj_big", "shot", t_id_list,  ["eps.eps_name", "shot.shot"])
    #print t_tw.task.get_dir("proj_big", "shot", t_id_list,  ["layout_work", "layout_approve"])
    #print t_tw.task.get_field_and_dir("proj_big", "shot",  t_id_list,  ["eps.eps_name", "shot.shot"], ["layout_work", "layout_approve"])
    #print t_tw.task.get_makedirs("proj_big", "shot", t_id_list)
    #print t_tw.task.get_submit_filebox("proj_big", "shot", t_id_list[0])
    #print t_tw.task.get_sign_filebox("proj_big", "shot", t_id_list[0], "maya_playblast")
    #print t_tw.task.get_filebox("proj_big", "shot", t_id_list[0], u"67B9A8CF-9DAE-8E05-342E-9E44C69976C2")
    #print t_tw.task.set("proj_big", "shot",  t_id_list,  {"task.start_date":"2018-02-02"})
    #print t_tw.task.delete("proj_big", "shot", t_id_list)
    #print t_tw.task.create("proj_big", "shot", "4E027BE9-2FEA-B65B-1EA2-B0E126BD9A3E", "3429200E-6801-4FD8-A742-8F2767674FB2", "Layout", "1110c3da-3444-4f37-a7fa-04846da3c879")
    #print t_tw.task.download_image("proj_big", "shot", t_id_list, "task.image")
    #print t_tw.task.set_image("proj_big", "shot", t_id_list, "shot.image", u"z:/png/test001.png")
    #print t_tw.task.count("proj_big", "shot", [  ["eps.eps_name", "=", "EP01"] ])
    #print t_tw.task.distinct("proj_big", "shot", [], "eps.eps_name", ["eps.eps_name"])
    #print t_tw.task.assign("proj_big", "shot", t_id_list, "87db8934-e479-4f00-89a7-5a59df0d9130")
    #print t_tw.task.submit("proj_big", "shot", t_id_list[0], [u"z:/png/test001.png"], u"submit png")
    #print t_tw.task.update_flow("proj_big", "shot", t_id_list[0], "task.leader_status","Retake", u"Retake png")

    #---------------note-----------------
    #print t_tw.note.fields()
    #t_id_list=t_tw.note.get_id("proj_big", [ ["module","=", "shot"], ["module_type","=", "task"] ])
    #print t_id_list
    #print t_tw.note.get("proj_big", t_id_list, ["#id", "text"])
    #print t_tw.note.create("proj_big", "shot", "task", ["E2083F3E-BF64-C3BA-79CE-DB5734A7BFB9"], "test note")
    
    
    #--------------filebox---------------
    #print t_tw.filebox.fields()
    #t_id_list=t_tw.filebox.get_id("proj_big", [ ["#pipeline_id", "=", "3429200E-6801-4FD8-A742-8F2767674FB2"] ])
    #print t_id_list
    #print t_tw.filebox.get("proj_big", t_id_list, ["title", "#id"])
    
    
    #--------------field---------------
    #print t_tw.field.type()
    #print t_tw.field.create("proj_big", "shot", "info", u"测数据", u"test_data_a", "test_data_a", "int")
    
    
    #---------------plugin------------------
    #print t_tw.plugin.fields()
    #t_id_list=t_tw.plugin.get_id([ ["type","=","menu"], ["name", "=", "test"] ])
    #print t_id_list
    #print t_tw.plugin.get(t_id_list, ["name", "argv"])
    #print t_tw.plugin.get_argvs(t_id_list[0])
    #print t_tw.plugin.set_argvs(t_id_list[0], {"ss" :"dd"})
    
    
    #---------------pipeline------------------
    #print t_tw.pipeline.fields()
    #t_id_list=t_tw.pipeline.get_id("proj_big", [ ["module", "=", "shot"], ["module_type","=", "task"] ])
    #print t_id_list
    #print t_tw.pipeline.get("proj_big", t_id_list, ["entity_name"])
    
    
    #---------------history------------------
    #print t_tw.history.fields()
    #t_id_list=t_tw.history.get_id("proj_big", [ ["module","=", "shot"], ["module_type", "=", "task"] ])
    #print t_id_list
    #print t_tw.history.get("proj_big", t_id_list, ["status", "text"])
    #print t_tw.history.count("proj_big", [ ["module","=", "shot"], ["module_type", "=", "task"] ])
    
    #---------------link------------------
    #t_link_id_list=t_tw.info.get_id("proj_big", "asset", [["asset.asset_name", "=", "daxiongtu"]])
    #t_id_list=t_tw.task.get_id("proj_big", "shot", [ ["eps.eps_name", "=", "EP01"],["shot.shot", "=", "sc001"], ["task.task_name", "=", "Layout"]])    
    #print t_tw.link.get_asset("proj_big", "shot", "task", t_id_list[0])
    #print t_tw.link.link_asset("proj_big", "shot", "task", t_id_list, t_link_id_list)
    #print t_tw.link.unlink_asset("proj_big", "shot", "task", t_id_list, t_link_id_list)
    
    
    #---------------software------------------
    #print t_tw.software.types()
    #print t_tw.software.get_path("proj_big", "hiero")
    #print t_tw.software.get_with_type("proj_big", "nuke")
    
    
    #---------------api_data------------------
    #print t_tw.api_data.set("proj_big", "test", "data")
    #print t_tw.api_data.get("proj_big", "test")
    
    
    #---------------version------------------
    #print t_tw.version.fields()
    #t_id_list=t_tw.version.get_id("proj_big", [])
    #print t_id_list
    #print t_tw.version.get("proj_big", t_id_list, ["#id", "filename"])
    #print t_tw.version.create("proj_big", u"E2083F3E-BF64-C3BA-79CE-DB5734A7BFB9", "v1", [u"z:/test.png"], ["/web/test.png"], "work")
    
    
    #---------------link_entity------------------
    #print t_tw.link_entity.fields()
    #print t_tw.link_entity.get_name("proj_big", u"E2083F3E-BF64-C3BA-79CE-DB5734A7BFB9")
    #print t_tw.link_entity.get("proj_big", [ ["module", "=", "shot"], ["module_type", "=", "task"] ])
    
    
    #---------------timelog------------------
    #print t_tw.timelog.fields()
    #t_id_list=t_tw.timelog.get_id("proj_big", [ ["module", "=", "shot"], ["module_type", "=", "task"] ])
    #print t_id_list
    #print t_tw.timelog.get("proj_big", t_id_list, ["#id", "use_time", "date", "create_by"], "5000",["date"])
    #print t_tw.timelog.create("proj_big", "E2083F3E-BF64-C3BA-79CE-DB5734A7BFB9", "shot", "task", "01:20", "2018-06-20", u"test data")
    #print t_tw.timelog.set_one("proj_big", "FCF07F64-26E7-9360-0BBD-6F25E71F652E", {"text": "test again data2"})