#coding:utf-8
"""
  Author:  shiming
  Purpose: 上传到CgTeamWork服务器
  Created: 2018-03-13
"""
import os
import sys
import traceback



#加载ct_plu库
t_base_path=unicode(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/")
if t_base_path not in sys.path:
    sys.path.append(t_base_path)
try:
    from cgtw import *
    import ct_plu
except Exception,e:
    print traceback.format_exc()    


#ct_base类名是固定的
class ct_base(ct_plu.extend):
    def __init__(self):
        ct_plu.extend.__init__(self)#继承
    
    def get_filebox_info(self, a_tw, a_db, a_module, a_module_type, a_task_id, a_filebox_id):
        t_os=a_tw.sys().get_sys_os()
        dic={"db":a_db, "module":a_module, "module_type":a_module_type, "task_id": a_task_id, "filebox_id":a_filebox_id, "os":t_os}
        res=a_tw.con()._send("c_file","qt_filebox_get_one_with_id", dic)
        if isinstance(res, dict):
            return res
        return False
    
    #重写run,外部调用
    def run(self, a_dict_data):
        t_argv=ct_plu.argv(a_dict_data)
        t_db=t_argv.get_sys_database()
        t_module=t_argv.get_sys_module()
        t_module_type=t_argv.get_sys_module_type()
        t_id_list=t_argv.get_sys_id()
        t_filebox_id=t_argv.get_sys_filebox_id()
        t_sou_file_list=t_argv.get_sys_file()
        t_des_file_list=t_argv.get_sys_des_file()
        t_version_id=t_argv.get_version_id()
        
        t_drag_in_upload_to_server_action=t_argv.get_filebox_key("action")
        try:
            t_tw = tw()
            #取文件框信息
            filebox_info=self.get_filebox_info(t_tw, t_db, t_module, t_module_type, t_id_list[0], t_filebox_id)
            if filebox_info==False or not filebox_info.has_key("server"):
                return self.ct_false("Get filebox info error")
            t_server=filebox_info["server"]
            
            #发送到queue
            t_action="upload"
            if unicode(","+t_drag_in_upload_to_server_action+",").find(",convert_before_upload,")!=-1:
                t_action="convert_movie_to_mp4"
                
            if unicode(","+t_drag_in_upload_to_server_action+",").find(",convert_image_before_upload,")!=-1:
                t_action="convert_image_to_image"            
            
            if unicode(","+t_drag_in_upload_to_server_action+",").find(",sequence_output_video,")!=-1:
                t_action="convert_seq_image_to_mov" 
                
            for i in range(len(t_sou_file_list)):
                t_name=os.path.basename(t_des_file_list[i])
                upload_list=[{"sou":t_sou_file_list[i], "des":unicode(t_des_file_list[i]).replace(t_server, "/")}]
                t_dic={'name':t_name, 'task': [{"action":t_action, "is_contine":True, "data_list":upload_list, "db":t_db, "module":t_module, "module_type":t_module_type, "task_id":t_id_list[0], "version_id":t_version_id}]}
                t_tw.local_con._send("queue_widget", "add_task", {"task_data":t_dic}, "send") 
            
            return self.ct_true()
            
        except Exception,e:
            #print traceback.format_exc()
            return self.ct_false(traceback.format_exc())
        
if __name__ == "__main__":
    #调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict=ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)

