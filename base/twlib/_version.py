# coding: utf-8
import os,sys,json
from _lib import _lib
class _version:
    
    @staticmethod
    def get_id(a_fun, a_db, a_filter_list, a_limit="5000"):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_filter_list, list) or not isinstance(a_limit, (str, unicode)) :
            raise Exception("_version.get_id argv error,  must be( str,list, str)")
        t_id_list=[]
        t_data={"db":a_db, "field_array":["#id"], "filter_array":a_filter_list, "limit":a_limit}
        t_data_list=a_fun("c_version", "get_with_filter", t_data)
        for data in t_data_list:
            if isinstance(data, list) and len(data)==1:
                t_id_list.append(data[0])
        return t_id_list
                
    
    @staticmethod
    def get(a_fun, a_db, a_id_list, a_field_list, a_limit="5000"):
        if not isinstance(a_db, (str, unicode)) or  not isinstance(a_id_list, list) or not isinstance(a_field_list, list) or \
           not isinstance(a_limit, (str, unicode)) :
            raise Exception("_version.get argv error,  must be( str,list, list, str)")  
        if len(a_id_list)==0 or len(a_field_list)==0:
            return []
        t_field_list=[]
        t_field_list=t_field_list+a_field_list
        t_field_list.append("#id")        
        t_data={"db":a_db, "field_array":t_field_list, "filter_array":[ ["#id", "in", a_id_list]], "limit":a_limit}
        t_data_list=a_fun("c_version", "get_with_filter", t_data)   
        return _lib.format_data(t_data_list, t_field_list)
    

    @staticmethod
    def create(a_fun, a_db, a_link_id,  a_version, a_local_path_list=[], a_web_path_list=[], a_sign="", a_image_list=[], a_from_version=""):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_link_id, (str, unicode)) or not isinstance(a_version, (str, unicode)) or not isinstance(a_local_path_list, list) or \
           not isinstance(a_web_path_list, list) or not isinstance(a_sign, (str, unicode)) or not isinstance(a_image_list, list) or not isinstance(a_from_version, (str, unicode)):
            raise Exception("_version.create argv error,  must be( str,str,str,list,list,str,list,str)")
        t_filename=[]
        for a_local_path in a_local_path_list:
            t_basename=os.path.basename(a_local_path)
            t_filename.append(t_basename)

        is_upload_web="N"
        if len(a_web_path_list)!=0:
            is_upload_web="Y"
        t_dic={"#link_id":a_link_id, "version":a_version,  "filename":t_filename, "local_path":a_local_path_list, "web_path":a_web_path_list, "sign":a_sign, "image":a_image_list, "from_version":a_from_version, "is_upload_web":is_upload_web}
        return _version._create(a_fun, a_db, t_dic)
    
    @staticmethod
    def _create(a_fun, a_db, a_field_data_dic):
        if isinstance(a_field_data_dic, dict)==False:
            raise Exception("_version._create, argv error(str, dict)")
        return a_fun("c_version", "create", {"db":a_db, "field_data_array":a_field_data_dic})    

    @staticmethod
    def fields():
        #t_field={
        #"#id": u"id",
        #"#link_id": u"关联的任务id",
        #"sign": u"标识",
        #"filename": u"文件名",
        #"local_path": u"本地路径",
        #"web_path": u"在线路径",
        #"version": u"版本",
        #"from_version": u"从版本更改"
        #}
        return ["#id", "#link_id", "sign", "filename", "local_path", "web_path", "version", "from_version"]