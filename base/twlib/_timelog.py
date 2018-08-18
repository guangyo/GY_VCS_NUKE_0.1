# coding: utf-8
import os,sys,json
from _lib import _lib
class _timelog:
    
    @staticmethod
    def get_id(a_fun, a_db, a_filter_list, a_limit="5000"):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_filter_list, list) or not isinstance(a_limit, (str, unicode)) :
            raise Exception("_timelog.get_id argv error,  must be( str,list, str)")
        t_id_list=[]
        t_data={"db":a_db, "field_array":["#id"], "filter_array":a_filter_list, "limit":a_limit}
        t_data_list=a_fun("c_time_log", "get_with_filter", t_data)
        for data in t_data_list:
            if isinstance(data, list) and len(data)==1:
                t_id_list.append(data[0])
        return t_id_list
                
    
    @staticmethod
    def get(a_fun, a_db, a_id_list, a_field_list, a_limit="5000", a_order_list=[]):
        if not isinstance(a_db, (str, unicode)) or  not isinstance(a_id_list, list) or  not isinstance(a_order_list, list) or not isinstance(a_field_list, list) or \
           not isinstance(a_limit, (str, unicode)) :
            raise Exception("_timelog.get argv error,  must be( str,list, list, str, list)")  
        if len(a_id_list)==0 or len(a_field_list)==0:
            return []
        t_field_list=[]
        t_field_list=t_field_list+a_field_list
        t_field_list.append("#id")        
        t_data={"db":a_db, "field_array":t_field_list, "filter_array":[ ["#id", "in", a_id_list]], "order_field_array":a_order_list, "limit":a_limit}
        t_data_list=a_fun("c_time_log", "get_with_filter", t_data)   
        return _lib.format_data(t_data_list, t_field_list)
    @staticmethod
    def set_one(a_fun, a_db, a_id, a_data_dict):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_id, (str, unicode)) or not isinstance(a_data_dict, dict):
            raise Exception("_timelog.set_one argv error,  must be( str,str,dict)")

        return a_fun("c_time_log", "set_one_with_id", {"db":a_db, "id":a_id, "field_data_array":a_data_dict})      

    @staticmethod
    def create(a_fun, a_db, a_task_id, a_module, a_module_type, a_use_time, a_date, a_text):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_task_id, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_use_time, (str, unicode)) or not isinstance(a_date, (str, unicode)) or not isinstance(a_text, (str, unicode)):
            raise Exception("_timelog.create argv error,  must be( str,str,str,str,str,str,str)")

        a_field_data_dic={"#task_id":a_task_id, "module":a_module,  "module_type":a_module_type, "use_time":a_use_time, "date":a_date, "text":a_text}
        return a_fun("c_time_log", "create", {"db":a_db, "field_data_array":a_field_data_dic})    
    

    @staticmethod
    def fields():
        #t_field={
        #"#id": u"id",
        #"#task_id": u"关联的任务id",
        #"module": u"模块",
        #"module_type": u"模块类型",
        #"use_time": u"用时",
        #"date": u"日期",
        #"text": u"内容",
        #"create_by": u"创建人员"
        #}
        return ["#id", "#task_id", "module", "module_type", "use_time", "date", "text", "create_by"]