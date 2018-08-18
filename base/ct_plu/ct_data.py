# -*- coding: utf-8 -*-
import os
import sys


class ct_data():

    #a_data可以为任意类型的变量
    def error(self, a_data=""):
        return {"code":'0', "data":a_data}
    
    #a_data可以为任意类型的变量
    def msg(self, a_data=""):
        return {"code":'1', "data":a_data}
    
    #a_data可以为任意类型的变量,用于停止后续的动作
    def stop_next(self, a_data=""):
        return {"code":'2', "data":a_data}
    
    #是否停止后续动作
    def is_stop_next(self, a_dict):
        if not isinstance(a_dict, dict):
            return False
        if a_dict.has_key("code")==False:
            return False
        if a_dict["code"]=="2":
            return True
        return False        

    def has_false(self, a_dict):
        if not isinstance(a_dict, dict):
            return False
        if a_dict.has_key("code")==False:
            return False
        if a_dict["code"]=="0":
            return True
        return False
    

    

    