# coding: utf-8
import os,sys,json
from _lib import _lib
class _module:
    
    @staticmethod
    def get_id(a_fun, a_db, a_module, a_module_type, a_filter_list, a_limit="5000", a_start_num=""):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_filter_list, list) or not isinstance(a_limit, (str, unicode)) or not isinstance(a_start_num, (str, unicode)):
            raise Exception("_module.get_id argv error,  must be( str,str,str,list, str, str)")
        t_id_list=[]
        t_id_sign=_module.__get_id_field(a_module, a_module_type)
        t_filter_list=_module.__change_filter(a_module, a_module_type,  a_filter_list)
        t_data={"db":a_db, "module":a_module, "module_type":a_module_type, "sign_array":[t_id_sign], "sign_filter_array":t_filter_list, "limit":a_limit, "order_sign_array":[], "start_num":a_start_num}
        t_data_list=a_fun("c_orm", "get_with_filter", t_data)
        for data in t_data_list:
            if isinstance(data, list) and len(data)==1:
                t_id_list.append(data[0])
        return t_id_list
                
    
    @staticmethod
    def get(a_fun, a_db, a_module, a_module_type, a_id_list, a_field_sign_list, a_limit="5000", a_order_sign_list=[]):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list) or not isinstance(a_field_sign_list, list) or not isinstance(a_limit, (str, unicode)) or not isinstance(a_order_sign_list, list):
            raise Exception("_module.get argv error,  must be( str,str,str,list, list, str, list)")  
        if len(a_id_list)==0:
            return []
        t_id_sign=_module.__get_id_field(a_module, a_module_type)
        t_field_sign_list=[]
        t_field_sign_list=t_field_sign_list+a_field_sign_list
        t_field_sign_list.append(t_id_sign)
        t_data_list=a_fun("c_orm", "get_in_id", {"db":a_db, "module":a_module, "module_type":a_module_type, "sign_array":t_field_sign_list, "id_array":a_id_list, "limit":a_limit, "order_sign_array":a_field_sign_list})
        t_result_list=[]
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

            t_result_list.append(t_tmp_dict)
        return t_result_list        
        
    
    @staticmethod
    def get_one(a_fun, a_db, a_module, a_module_type, a_id, a_field_sign_list):
        pass        
    
    @staticmethod
    def set(a_fun, a_db, a_module, a_module_type, a_id_list, a_sign_data_dict):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list) or not isinstance(a_sign_data_dict, dict):
            raise Exception("_module.set argv error,  must be( str,str,str,list, dict)")  
        if len(a_id_list)==0:
            return False
        return a_fun("c_orm", "set_in_id", {"db":a_db, "module":a_module, "module_type":a_module_type, "id_array":a_id_list, "sign_data_array":a_sign_data_dict})
    
    @staticmethod
    def delete(a_fun, a_db, a_module, a_module_type, a_id_list):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list):
            raise Exception("_module.delete argv error,  must be( str,str,str,list)")  
        if len(a_id_list)==0:
            return False
        
        if unicode(a_db).lower().strip()=="public" and a_module in ["project"]:
            raise Exception("_module.delete , can not use to public.project")
        
                
        return a_fun("c_orm", "del_in_id", {"db":a_db, "module":a_module, "module_type":a_module_type, "id_array":a_id_list})
    
    @staticmethod
    def get_dir(a_fun, a_db, a_module, a_module_type, a_id_list, a_folder_sign_list):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list) or not isinstance(a_folder_sign_list, list):
            raise Exception("_module.get_dir argv error,  must be( str,str,str,list, list)")  
        
        if unicode(a_db).lower().strip()=="public":
            raise Exception("_module.get_dir , can not use to public database")
                
        if len(a_id_list)<=0:
            return []     
        t_os=_lib.get_os()
        t_data_list=a_fun("c_folder",  "get_replace_path_in_sign", {"db":a_db, "module":a_module, "module_type":a_module_type, "task_id_array":a_id_list, "os":t_os, "sign_array":a_folder_sign_list})
        t_result_list=[]

        for key in t_data_list.keys():
            t_tmp_dict={}
            t_tmp_dict["id"]=key
            for i in range(len(a_folder_sign_list)):
                if len(a_folder_sign_list)!=len(t_data_list[key]):
                    t_tmp_dict[a_folder_sign_list[i]]=""
                t_tmp_dict[a_folder_sign_list[i]]=t_data_list[key][i]
            t_result_list.append(t_tmp_dict)
        return t_result_list    
    
    @staticmethod
    def get_field_and_dir(a_fun, a_db, a_module, a_module_type, a_id_list, a_field_sign_list, a_folder_sign_list):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list) or not isinstance(a_field_sign_list, list) or not isinstance(a_folder_sign_list, list):
            raise Exception("_module.get_field_and_dir argv error,  must be( str,str,str,list,list,list)")
        
        if unicode(a_db).lower().strip()=="public":
            raise Exception("_module.get_field_and_dir , can not use to public database")
                
        if len(a_id_list)<=0:
            return []            
        t_field_data=_module.get(a_fun, a_db, a_module, a_module_type, a_id_list, a_field_sign_list)
        t_folder_data=_module.get_dir(a_fun, a_db, a_module, a_module_type, a_id_list,a_folder_sign_list)
        if t_field_data==False or t_folder_data==False:
            raise Exception("_module.get_field_and_dir get data error")
        t_result_list=[]
        for t_field in t_field_data:
            tmp_dict=t_field
            is_exist=False
            for t_folder in t_folder_data:
                if t_field["id"]==t_folder["id"]:
                    is_exist=True
                    tmp_dict.update(t_folder.items())
                    t_result_list.append(tmp_dict)
                    break
            if is_exist==False:
                return []
        else:
            return t_result_list        
    
    @staticmethod
    def download_image(a_fun, a_http_ip, a_cgtw_path, a_token, a_db, a_module, a_module_type, a_id_list, a_field_sign, a_is_small=True, a_local_path=""):
        if not isinstance(a_http_ip, (str, unicode)) or not isinstance(a_cgtw_path, (str, unicode)) or not isinstance(a_token, (str, unicode)) or \
           not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list) or not isinstance(a_field_sign, (str, unicode)) or not isinstance(a_is_small, bool) or not isinstance(a_local_path, (str, unicode)):
            raise Exception("_module.download_image argv error,  must be( str,str,str,list,str,bool,str)")
        
        t_os=_lib.get_os()
        if a_cgtw_path not in sys.path:
            sys.path.append(a_cgtw_path)        
        import ct        
        t_localpath=a_local_path
        if t_localpath.strip()=="":
            t_localpath=ct.com().get_tmp_path()
        if not os.path.exists(t_localpath):
            try:
                os.mkdir(t_localpath)
            except Exception, e:
                raise Exception(e)
        t_data_list=_module.get(a_fun, a_db, a_module, a_module_type, a_id_list, [a_field_sign])
        t_image_data=[]
        t_size="max"
        if a_is_small==True:
            t_size="min"
        t_http=ct.http(a_http_ip, a_token)
        for data in t_data_list:
            t_download_list = []
            t_image_json=_lib.decode(data[a_field_sign])
            if t_image_json != None and isinstance(t_image_json, dict):
                for t_image in t_image_json[t_size]:
                    t_local_file=t_localpath+t_image
                    t_result=t_http.download(t_image, t_local_file)
                    if t_result==False:
                        t_local_file=""
                    t_download_list.append(t_local_file)
            t_image_data.append({"id":data["id"], a_field_sign:t_download_list})
        return t_image_data    
    
    @staticmethod
    def set_image(a_fun, a_http_ip, a_cgtw_path, a_token, a_db, a_module, a_module_type, a_id_list, a_field_sign, a_img_path, a_compress="1080"):
        if not isinstance(a_http_ip, (str, unicode)) or not isinstance(a_cgtw_path, (str, unicode)) or not isinstance(a_token, (str, unicode)) or \
           not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list) or not isinstance(a_field_sign, (str, unicode))  or not isinstance(a_compress, (str, unicode)):
            raise Exception("_module.set_image argv error,  must be( str,str,str,list,str,str)")        
        
        a_img_path_list = []
        if isinstance(a_img_path, (str, unicode)):
            if a_img_path.strip()=="":
                #清空
                return _module.set(a_fun, a_db, a_module, a_module_type, a_id_list, {a_field_sign:""})
            a_img_path_list.append(a_img_path)
        else:
            a_img_path_list = a_img_path
            
        if not isinstance(a_img_path_list, (list)):
            raise Exception("_module.set_image argv error , a_img_path type in (list/str/unicode)")

        t_big_list = []
        t_small_list = []
        if a_cgtw_path not in sys.path:
            sys.path.append(a_cgtw_path)
        import ct
        t_http=ct.http(a_http_ip, a_token)
        for t_image_file in a_img_path_list:
            res=t_http.upload_project_img(t_image_file, a_db, "project", None, a_compress)
            if res.has_key("max") and res.has_key("min"):
                t_big_list.append(res["max"])
                t_small_list.append(res["min"])
        return _module.set(a_fun, a_db, a_module, a_module_type, a_id_list, {a_field_sign:_lib.encode({"max":t_big_list, "min":t_small_list}) })
    
    @staticmethod
    def count(a_fun, a_db, a_module, a_module_type, a_filter_list):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_filter_list, list):
            raise Exception("_module.count argv error,  must be( str,str,str,list)")        
        t_filter_list=_module.__change_filter(a_module, a_module_type,  a_filter_list)
        return a_fun("c_orm", "get_count_with_filter", {"db":a_db, "module":a_module, "module_type":a_module_type, "sign_filter_array":a_filter_list})
    
    @staticmethod
    def distinct(a_fun, a_db, a_module, a_module_type, a_filter_list, a_field_sign, a_order_sign_list=[]):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_filter_list, list) or not isinstance(a_field_sign, (str, unicode)) or not isinstance(a_order_sign_list, list) :
            raise Exception("_module.distinct argv error,  must be( str,str,str,list, str,list)")             
        t_filter_list=_module.__change_filter(a_module, a_module_type,  a_filter_list)
        t_data_list=a_fun("c_orm", "get_distinct_with_filter", {"db":a_db, "module":a_module, "module_type":a_module_type, "distinct_sign":a_field_sign, "sign_filter_array":a_filter_list, "order_sign_array":a_order_sign_list})	
        t_result_list=[]
        for tmp in t_data_list:
            t_result_list.append(tmp[0])
        return t_result_list
    
    @staticmethod
    def create(a_fun, a_db, a_module, a_module_type, a_sign_data_dict, a_is_return_id=False):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_sign_data_dict, dict) or not isinstance(a_is_return_id, bool):
            raise Exception("_module.create argv error,  must be( str,str,str,dict,bool)")
        
        if unicode(a_db).lower().strip()=="public" and unicode(a_module).lower().strip() in ["account", "project"]:
            raise Exception("_module.create , can not use to (db: public, module:<account, project> )")
                
        if a_module_type=="task":
            raise Exception("_module.create,  only use to info module")
        
        if a_module=="asset":
            a_sign_data_dict=_module.__change_asset_data(a_fun, a_db, a_sign_data_dict)

        elif a_module=="shot":
            a_sign_data_dict=_module.__change_shot_data(a_fun, a_db, a_sign_data_dict)
        
        if not a_is_return_id:
            return a_fun("c_orm", "create", {"db":a_db, "module":a_module, "module_type":a_module_type, "sign_data_array":a_sign_data_dict})
        else:
            t_id=_lib.uuid()
            a_sign_data_dict[a_module+".id"]=t_id
            res=a_fun("c_orm", "create", {"db":a_db, "module":a_module, "module_type":a_module_type, "sign_data_array":a_sign_data_dict})
            if res==True:
                return t_id
            else:
                return False
    
    
    @staticmethod
    def get_makedirs(a_fun, a_db, a_module, a_module_type, a_id_list):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list):
            raise Exception("_module.get_makedirs argv error,  must be( str,str,str,list)")
        
        if unicode(a_db).lower().strip()=="public":
            raise Exception("_module.get_makedirs , can not use to public database")
        
        if len(a_id_list)==0:
            return False
        
        
        t_os=_lib.get_os()
        #怕选择的要创建的目录太多的时候。进行分ID取数据
        t_page_num=100#每次的条数
        t_num=len(a_id_list)/t_page_num #循环的次数
        t_module_num=len(a_id_list)%t_page_num #取模
        if t_module_num>0:
            t_num=t_num+1
        
        t_all_data_lis=[]                    
        for i in range(t_num):
            temp_id_lis=a_id_list[i*t_page_num: (i+1)*t_page_num]
            res=a_fun("c_folder","get_create_folder_data", {"db":a_db, "module":a_module, "module_type":a_module_type, "os":t_os, "task_id_array":temp_id_lis})
            t_all_data_lis=t_all_data_lis+res
                
        return t_all_data_lis    
    
    @staticmethod
    def create_task(a_fun, a_db, a_module, a_module_type, a_join_id, a_pipeline_id, a_task_name, a_flow_id):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_join_id, (str, unicode)) or not isinstance(a_pipeline_id, (str, unicode)) or not isinstance(a_task_name, (str, unicode)) or not isinstance(a_flow_id, (str, unicode)):
            raise Exception("_module.create_task argv error,  must be( str,str,str,str,str,str,str)")  
        if unicode(a_join_id).strip()=="" or unicode(a_pipeline_id).strip()=="" or unicode(a_task_name).strip()=="" :
            raise Exception("_module.create_task argv error,  can not empty( a_join_id, a_pipeline_id, a_task_name)")  
        
        t_post_data={"db":a_db, "module":a_module, "module_type":a_module_type, "join_id":a_join_id, "pipeline_id":a_pipeline_id, "flow_id":a_flow_id, "task_name":a_task_name};
        return a_fun("c_orm","create_task", t_post_data)        
    
    @staticmethod
    def assign(a_fun, a_db, a_module, a_module_type, a_id_list, a_assign_account_id, a_start_date="", a_end_date=""):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list) or not isinstance(a_assign_account_id, (str, unicode)) or not isinstance(a_start_date, (str, unicode)) or not isinstance(a_end_date, (str, unicode)):
            raise Exception("_module.assign argv error,  must be( str,str,str,list,str,str,str)")  
        if len(a_id_list)==0:
            return False
        return a_fun("c_work_flow", "assign_to", {'db':a_db, 'module':a_module, 'module_type':a_module_type, 'assign_account_id':a_assign_account_id, 'start_date':a_start_date, 'end_date':a_end_date, 'task_id_array':a_id_list})
        
    @staticmethod
    def submit(a_fun, a_account_id, a_db, a_module, a_module_type, a_id, a_file_path_list, a_note="",a_path_list=[]):
        if not isinstance(a_account_id, (str, unicode)) or not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id, (str, unicode)) or not isinstance(a_file_path_list, list) or not isinstance(a_note, (str, unicode)) or not isinstance(a_path_list, list):
            raise Exception("_module.submit argv error,  must be( str,str,str,str,str,list,str,list)")
        if unicode(a_id).strip()=="":
            return False
        if len(a_file_path_list)==0 and len(a_path_list)==0:
            return False
        t_note=json.dumps({"data":a_note, "image":[]})
        if a_note.strip()=="":
            t_note=""   
        if a_path_list==[]:
            a_path_list=a_file_path_list
        t_submit_file_path_array={"path":a_path_list,"file_path":a_file_path_list}

        basename_list=[]
        for n in a_file_path_list:
            basename_list.append(os.path.basename(n))

        import uuid
        version_id=unicode(uuid.uuid4())
        t_dic={"#link_id":a_id, "version":"",  "filename":basename_list, "local_path":a_path_list, "web_path":[], "sign":"Api Submit", "image":"", "from_version":"", "is_upload_web":"N", "#id":version_id}
        res=a_fun("c_version", "create", {"db":a_db, "field_data_array":t_dic})
        if res!=True:
            return False
        return a_fun("c_work_flow","submit",{"db":a_db,"module":a_module,"module_type":a_module_type, "task_id":a_id,"account_id":a_account_id,"submit_file_path_array":t_submit_file_path_array,"text":t_note, "version_id":version_id})
        
        
    
    @staticmethod
    def update_flow(a_fun, a_db, a_module, a_module_type, a_id, a_field_sign, a_status, a_note=""):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id, (str, unicode)) or not isinstance(a_field_sign, (str, unicode)) or not isinstance(a_status, (str, unicode)) or not isinstance(a_note, (str, unicode)):
            raise Exception("_module.update_flow argv error,  must be( str,str,str,str,str,str,str)")  
        if unicode(a_id).strip()=="":
            return False    
        
        t_note_data=""
        if a_note.strip()!="":
            t_note_data=json.dumps({"data":a_note, "image":[]})
        return  a_fun("c_work_flow","python_update_flow", {"db":a_db, "module":a_module, "module_type":a_module_type,  "field_sign":a_field_sign, "text":t_note_data, "status":a_status, "task_id":a_id})
    
    @staticmethod
    def get_submit_filebox(a_fun, a_db, a_module, a_module_type, a_id):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id, (str, unicode)):
            raise Exception("_module.get_submit_filebox argv error,  must be( str,str,str,str)")  
        if unicode(a_id).strip()=="":
            return []
        t_os=_lib.get_os()
        return a_fun("c_file","filebox_get_submit_data",{"db":a_db,"module":a_module,"module_type":a_module_type, "task_id":a_id, "os":t_os})
        
    @staticmethod
    def get_sign_filebox(a_fun, a_db, a_module, a_module_type, a_id, a_filebox_sign):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id, (str, unicode)) or not isinstance(a_filebox_sign, (str, unicode)):
            raise Exception("_module.get_sign_filebox argv error,  must be( str,str,str,str,str)")  
        
        if unicode(a_db).lower().strip()=="public":
            raise Exception("_module.get_sign_filebox , can not use to public database")
        
                
        if unicode(a_id).strip()=="":
            return []
        t_os=_lib.get_os()
        return a_fun("c_file","filebox_get_one_with_sign",{"db":a_db,"module":a_module,"module_type":a_module_type, "task_id":a_id, "os":t_os, "sign":a_filebox_sign})
        
    @staticmethod
    def get_filebox(a_fun, a_db, a_module, a_module_type, a_id, a_filebox_id):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id, (str, unicode)) or not isinstance(a_filebox_id, (str, unicode)):
            raise Exception("_module.get_filebox argv error,  must be( str,str,str,str,str)")  
        
        if unicode(a_db).lower().strip()=="public":
            raise Exception("_module.get_filebox , can not use to public database")
                
        if unicode(a_id).strip()=="":
            return []
        t_os=_lib.get_os()
        return a_fun("c_file","filebox_get_one_with_id",{"db":a_db, "module":a_module,"module_type":a_module_type, "task_id":a_id, "os":t_os, "filebox_id":a_filebox_id})
        
    @staticmethod
    def modules(a_fun, a_db, a_module_type):
        t_module_list=[]
        t_field_list=["module", "is_link_task"]
        t_data_list=a_fun("c_module","get_with_filter",{"db":a_db, "field_array":t_field_list,"filter_array":[["type","=", "info"]]})
        t_new_data_list=_lib.format_data(t_data_list, t_field_list)
        for i in t_new_data_list:
            t_module=i["module"]
            t_is_link_task=i["is_link_task"]
            if unicode(a_module_type).strip().lower()=="task" and unicode(t_is_link_task).strip().lower()!="y":
                continue
            t_module_list.append(t_module)
        return t_module_list
    
    #------------------------------------------------------------------------
    @staticmethod
    def __change_asset_data(a_fun, a_db, a_sign_data_dict):
        '''
        替换asset的创建数据
        '''
        if not a_sign_data_dict.has_key("asset.asset_name") and not a_sign_data_dict.has_key("asset.type_name"):
            raise Exception("_module.__change_asset_data, a_sign_data_dict must have key (asset.asset_name,  asset.type_name)")
        t_sign_data_dict=a_sign_data_dict.copy()
        t_type_id=a_fun("c_config","get_one_with_filter", {"table":a_db+".conf_type", "field":"#id", "filter_array":[ ["entity_name","=", t_sign_data_dict["asset.type_name"] ] ] })
        if t_type_id==False  or t_type_id=="":
            raise Exception("_module.__change_asset_data, it's not exist this asset type")
        t_sign_data_dict.update({"asset.type_name":t_type_id})
        return t_sign_data_dict
 
    @staticmethod
    def __change_shot_data(a_fun, a_db, a_sign_data_dict):
        '''
        替换shot的创建数据
        '''        
        if not a_sign_data_dict.has_key("eps.eps_name") and not a_sign_data_dict.has_key("eps.id") and not a_sign_data_dict.has_key("shot.shot"):
            raise Exception("_module.__change_shot_data, a_sign_data_dict must have key (eps.eps_name/eps.id,  shot.shot)")
        t_sign_data_dict=a_sign_data_dict.copy()
        if t_sign_data_dict.has_key("eps.eps_name"):
            t_eps_id=a_fun("c_orm", "get_one_with_filter", {"db":a_db, "module":"eps", "module_type": "info", "sign":"eps.id", "sign_filter_array":[ ["eps.eps_name", "=", t_sign_data_dict["eps.eps_name"] ] ] })
            if t_eps_id==False or t_eps_id=="":
                raise Exception("_module.__change_shot_data, it's not exist this eps" )
            t_sign_data_dict.pop("eps.eps_name")
        elif t_sign_data_dict.has_key("eps.id"):
            t_eps_id=t_sign_data_dict["eps.id"]
            t_sign_data_dict.pop("eps.id")
        else:
            raise Exception("_module.__change_shot_data, a_sign_data_dict must have key (eps.eps_name or eps.id)" )
        t_sign_data_dict.update({"shot.eps_name":t_eps_id})
        return t_sign_data_dict	 
    
    @staticmethod
    def __get_id_field(a_module, a_module_type):
        if a_module_type=="task":
            return "task.id"
        return a_module+".id"
    @staticmethod
    def __change_filter(a_module, a_module_type, a_filter_list):
        '''
        替换过滤
        '''
        if a_module_type=="task":
            if len(a_filter_list)!=0:
                t_filter_list=["(", ["task.module", "=", a_module], ")", "and", "("]+a_filter_list+[")"]    
            else:
                t_filter_list=[ ["task.module", "=", a_module] ] 
            return t_filter_list
        else:
            return a_filter_list