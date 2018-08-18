# coding: utf-8
import os,sys,json
from _lib import _lib
class _history:
    
    @staticmethod
    def get_id(a_fun, a_db, a_filter_list, a_limit="5000"):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_filter_list, list) or not isinstance(a_limit, (str, unicode)) :
            raise Exception("_history.get_id argv error,  must be( str,list, str)")
        t_id_list=[]
        t_data={"db":a_db, "field_array":["#id"], "filter_array":a_filter_list, "limit":a_limit}
        t_data_list=a_fun("c_history", "get_with_filter", t_data)
        for data in t_data_list:
            if isinstance(data, list) and len(data)==1:
                t_id_list.append(data[0])
        return t_id_list
                
    
    @staticmethod
    def get(a_fun, a_db, a_id_list, a_field_list, a_limit="5000", a_order_list=[]):
        if not isinstance(a_db, (str, unicode)) or  not isinstance(a_id_list, list) or not isinstance(a_field_list, list) or \
           not isinstance(a_limit, (str, unicode)) or not isinstance(a_order_list, list):
            raise Exception("_history.get argv error,  must be( str,list, list, str, list)")  
        if len(a_id_list)==0 or len(a_field_list)==0:
            return []
        t_field_list=[]
        t_field_list=t_field_list+a_field_list
        t_field_list.append("#id")        
        t_data={"db":a_db, "field_array":t_field_list, "filter_array":[ ["#id", "in", a_id_list]], "limit":a_limit, "order_field_array": a_order_list}
        t_data_list=a_fun("c_history", "get_with_filter", t_data)   
        return _lib.format_data(t_data_list, t_field_list)     
        
    
    @staticmethod
    def count(a_fun, a_db, a_filter_list):
        if not isinstance(a_db, (str, unicode))or not isinstance(a_filter_list, list):
            raise Exception("_history.count argv error,  must be( str,list)")        
        return a_fun("c_history", "count_with_filter", {"db":a_db, "filter_array":a_filter_list})

    @staticmethod
    def fields():
        #t_field={
        #"#id": u"id",
        #"#task_id": u"任务的ID",
        #"module":u"模块",
        #"module_type": u"模块类型",
        #"time":u"时间",
        #"status":u"状态",
        #"text":u"内容"
        #}
        return ["#id", "#task_id", "module", "module_type", "time", "status", "text"]