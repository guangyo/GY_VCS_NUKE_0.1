# coding: utf-8
import os,sys,json
from _lib import _lib
class _pipeline:
    
    @staticmethod
    def get_id(a_fun, a_db, a_filter_list):
        if not isinstance(a_db, (str, unicode))  or not isinstance(a_filter_list, list) :
            raise Exception("_pipeline.get_id argv error,  must be( str,list)")
        t_id_list=[]
        t_data={"db":a_db, "field_array":["#id"], "filter_array":a_filter_list}
        t_data_list=a_fun("c_pipeline", "get_with_filter", t_data)
        for data in t_data_list:
            if isinstance(data, list) and len(data)==1:
                t_id_list.append(data[0])
        return t_id_list
                
    @staticmethod
    def get(a_fun, a_db, a_id_list, a_field_list):
        if  not isinstance(a_db, (str, unicode))  or not isinstance(a_id_list, list) or not isinstance(a_field_list, list):
            raise Exception("_pipeline.get argv error,  must be( str,list, list)")  
        if len(a_id_list)==0 or len(a_field_list)==0:
            return []
        t_field_list=[]
        t_field_list=t_field_list+a_field_list
        t_field_list.append("#id")      
        t_data={"db":a_db, "field_array":t_field_list, "filter_array":[ ["#id", "in", a_id_list]]}
        t_data_list=a_fun("c_pipeline", "get_with_filter", t_data)   
        return _lib.format_data(t_data_list, t_field_list)
    
    @staticmethod
    def fields():
        #t_field={
        #"#id": u"id",
        #"entity_name": u"阶段名",
        #"module":"模块",
        #"module_type": u"模块类型",
        #}
        return ["#id", "entity_name", "module", "module_type"]