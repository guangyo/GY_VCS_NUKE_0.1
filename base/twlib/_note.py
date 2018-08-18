# coding: utf-8
import os,sys,json
from _lib import _lib
class _note:
    
    @staticmethod
    def get_id(a_fun, a_db, a_filter_list, a_limit="5000"):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_filter_list, list) or not isinstance(a_limit, (str, unicode)) :
            raise Exception("_note.get_id argv error,  must be( str,list, str)")
        t_id_list=[]
        t_data={"db":a_db, "field_array":["#id"], "filter_array":a_filter_list, "limit":a_limit}
        t_data_list=a_fun("c_note", "get_with_filter", t_data)
        for data in t_data_list:
            if isinstance(data, list) and len(data)==1:
                t_id_list.append(data[0])
        return t_id_list
                
    
    @staticmethod
    def get(a_fun, a_db, a_id_list, a_field_list, a_limit="5000", a_order_list=[]):
        if not isinstance(a_db, (str, unicode)) or  not isinstance(a_id_list, list) or not isinstance(a_field_list, list) or \
           not isinstance(a_limit, (str, unicode)) or not isinstance(a_order_list, list):
            raise Exception("_note.get argv error,  must be( str,list, list, str)")  
        if len(a_id_list)==0 or len(a_field_list)==0:
            return []
        t_field_list=[]
        t_field_list=t_field_list+a_field_list
        t_field_list.append("#id")        
        t_data={"db":a_db, "field_array":t_field_list, "filter_array":[ ["#id", "in", a_id_list]], "limit":a_limit, "order_field_array": a_order_list}
        t_data_list=a_fun("c_note", "get_with_filter", t_data)   
        return _lib.format_data(t_data_list, t_field_list)
    

    @staticmethod
    def create(a_fun, a_http_ip, a_cgtw_path, a_token, a_account_id, a_db, a_module, a_module_type, a_task_id_list, a_text, a_cc_acount_id="", a_image_list=[]):
        if not isinstance(a_http_ip, (str, unicode)) or not isinstance(a_cgtw_path, (str, unicode)) or not isinstance(a_account_id, (str, unicode)) or not isinstance(a_token, (str, unicode)) or \
           not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_task_id_list, list) or not isinstance(a_text, (str, unicode)) or not isinstance(a_cc_acount_id, (str, unicode)) or not isinstance(a_image_list, list):
            raise Exception("_note.create argv error,  must be( str,str,str,str,str,str,str,list,str,str,list)")
        if len(a_task_id_list)==0:
            return False
        
        t_os=_lib.get_os()
        image_list=[]
        if len(a_image_list)!=0:
            if a_cgtw_path not in sys.path:
                sys.path.append(a_cgtw_path)        
            import ct  
            t_http=ct.http(a_http_ip, a_token)                                
            for t_image_file in a_image_list:
                res=t_http.upload_project_img(t_image_file, a_db)
                if res.has_key("max") and res.has_key("min"):
                    image_list.append(res)                                
        return a_fun("c_note", "create", {"db":a_db, "cc_acount_id":a_cc_acount_id, "field_data_array":{"module":a_module,  "module_type":a_module_type, "#task_id":",".join(a_task_id_list), "text":{"data":a_text, "image":image_list}, "#from_account_id":a_account_id }})
 

    @staticmethod
    def fields():
        #t_field={
        #"#id": u"id",
        #"#task_id": u"关联的任务id",
        #"module": u"模块",
        #"module_type": u"模块类型",
        #"text": u"内容",
        #"create_time": u"创建时间",
        #"create_by": u"创建人员"
        #}
        return ["#id", "#task_id", "module", "module_type", "text", "create_time", "create_by"]