# coding: utf-8
import os,sys,json
from _lib import _lib
class _plugin:
    
    @staticmethod
    def get_id(a_fun, a_filter_list):
        if not isinstance(a_filter_list, list) :
            raise Exception("_plugin.get_id argv error,  must be( list)")
        t_id_list=[]
        t_data={"field_array":["#id"], "filter_array":a_filter_list}
        t_data_list=a_fun("c_plugin", "get_with_filter", t_data)
        for data in t_data_list:
            if isinstance(data, list) and len(data)==1:
                t_id_list.append(data[0])
        return t_id_list
                
    
    @staticmethod
    def get(a_fun, a_id_list, a_field_list):
        if not isinstance(a_id_list, list) or not isinstance(a_field_list, list):
            raise Exception("_plugin.get argv error,  must be(list, list)")  
        if len(a_id_list)==0 or len(a_field_list)==0:
            return []
        t_field_list=[]
        t_field_list=t_field_list+a_field_list
        t_field_list.append("#id")      
        t_data={"field_array":t_field_list, "filter_array":[ ["#id", "in", a_id_list]]}
        t_data_list=a_fun("c_plugin", "get_with_filter", t_data)   
        return _lib.format_data(t_data_list, t_field_list)
    
    @staticmethod
    def get_one(a_fun, a_id, a_field):
        if not isinstance(a_field, (list,str, unicode)) or not isinstance(a_id, (str, unicode)):
            raise Exception("_plugin.get_one argv error,  must be( str,str)")  

        t_field_list=[]
        if isinstance(a_field,list):
            t_field_list=t_field_list+a_field
        elif isinstance(a_field,(str,unicode)):
            t_field_list.append(a_field)
        t_field_list.append("#id")      
        t_data={"field_array":t_field_list, "filter_array":[ ["#id", "=", a_id]]}
        t_data_list=a_fun("c_plugin", "get_one_with_id", {"id":a_id, "field_array":t_field_list})   
        return _lib.format_data_to_dict(t_data_list, t_field_list)
    
    @staticmethod
    def get_argvs(a_fun, a_id):    
        if not isinstance(a_id, (str, unicode)):
            raise Exception("_plugin.get_argvs argv error,  must be( str )")     
        t_data_list=_plugin.get_one(a_fun, a_id, "argv")
        if t_data_list==False:
            raise Exception("_plugin.get_argvs get data error")
        t_argv=_lib.decode(t_data_list['argv'])
        if t_argv=="":
            return {}
        t_result_dict={}
        for key in t_argv.keys():
            t_result_dict[key]=t_argv[key]["value"]
        return t_result_dict
    
    @staticmethod
    def set_argvs(a_fun, a_id, a_argvs_dict):      
        if not isinstance(a_id, (str, unicode)) or not isinstance(a_argvs_dict, dict):
            raise Exception("_plugin.set_argvs argv error,  must be( str,dict)")          
        t_argv_dict=_plugin.__change_data_dict_for_set_argvs(a_argvs_dict)
        if t_argv_dict==False:
            return False
        t_json_str=_lib.encode(t_argv_dict)
        if t_json_str==False:
            return False    
        return a_fun("c_plugin","set_one_with_id",{"id":a_id,"field_data_array":{"argv":t_json_str}})

    @staticmethod
    def __change_data_dict_for_set_argvs(a_argvs_dict):
        if isinstance(a_argvs_dict,dict)==False:
            raise Exception("plugin.__change_data_dict_for_set_argvs argv error , argv must be dict")
        t_result_dict={}
        for key in a_argvs_dict.keys():
            t_result_dict[key]={"value":a_argvs_dict[key],"description":""}
        return t_result_dict

    @staticmethod
    def fields():
        #t_field={
        #"#id": u"id",
        #"name": u"插件名",
        #"type":"插件类型",
        #"argv": u"参数",
        #}
        return ["#id", "name", "type", "argv"]