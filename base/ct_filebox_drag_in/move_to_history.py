#coding:utf-8
"""
  Author:  shiming
  Purpose: 移动到历史
  Created: 2018-03-13
"""
import os
import sys
import traceback


#加载ct_plu库
t_base_path=unicode(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/")
t_cgtw_path = os.path.dirname( t_base_path ) + "/cgtw/"

if t_base_path not in sys.path:
    sys.path.append(t_base_path)
if not t_cgtw_path in sys.path:
    sys.path.append( t_cgtw_path )

try:
    from cgtw import *
    import ct_plu
    from ct_plu.qt import *
    import ct_ui
    import ct_lib
    import ct
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
    
    #判断是否在同一个目录,源和目标是否是同一个目录
    def is_has_same_folder(self, a_sou_list, a_des_list):
        if len(a_sou_list)>=1 and len(a_des_list)>=1 and len(a_sou_list)==len(a_des_list):
            for i in range(len(a_sou_list)):
                sou_dir=os.path.dirname(a_sou_list[i])
                des_dir=os.path.dirname(a_des_list[i])
                if sou_dir==des_dir:
                    return True
        return False   
    
    def common_move(self, a_current_path, a_sou_list, a_is_in_history_add_datetime, a_is_in_history_add_version, a_is_force_cover_no_message=False):
        #current_path指的是当前文件框的路径
        des_path=""
        new_des_list=[]
        new_sou_list=[]
        if len(a_sou_list)>0:
            for sou_file in a_sou_list:
                #判断文件是否存在
                if not os.path.exists(sou_file):
                    continue
                new_sou_list.append(sou_file)
                temp_sou_file=sou_file
                if ct.com().get_os()=="mac" and os.path.isdir(sou_file):
                    temp_sou_file=unicode(sou_file).rstrip("\\").rstrip("/")
                    
                if a_is_in_history_add_datetime=="y":
                    des_path=a_current_path+"/history/"+ct.com().now('%Y-%m-%d-%H-%M-%S')+"/"+os.path.basename(temp_sou_file)
                else:
                    des_path=a_current_path+"/history/"+os.path.basename(temp_sou_file)
                
                temp_des_file=des_path
                
                if a_is_in_history_add_version=="y":
                    temp_des_file=ct_lib.com().auto_add_version(des_path)
                
                if ct.com().get_os()=="mac" and os.path.isdir(sou_file):
                    temp_des_file=temp_des_file+"/"               
                new_des_list.append(temp_des_file)

            if len(new_sou_list)>0 and len(new_sou_list)==len(new_des_list):
                self.copy=ct_ui.copy_widget(new_sou_list, new_des_list, None, False, True, a_is_force_cover_no_message)
                if self.copy.exec_()==QDialog.Accepted:
                    return True
                else:
                    return False
        return True
    
    #移动提交文件
    def move_check_file_to_history(self, a_tw, a_db, a_module, a_module_type, a_task_id, a_is_in_history_add_datetime, a_is_in_history_add_version):
        res=a_tw.con()._send("c_orm", "get_with_filter",{"db":a_db, "module":a_module, "module_type":a_module_type, "sign_array":["task.submit_file_path"], "sign_filter_array":[["task.id", "=", a_task_id] ]})     
        if isinstance(res, list):
            for data_list in res:                
                if isinstance(data_list, list) and len(data_list)== 1:
                    #submit_file_path里面存有{file:[], file_path:[]},如果是提交文件，两个都一样，如果提交文件夹。file:[z:/aa]而file_path:[z:/aa/1.jpg]细到里面的文件
                    path_list=list(ct.json().get_data(data_list[0], "path"))
                    file_path_list=list(ct.json().get_data(data_list[0], "file_path"))
                    if len(file_path_list)>0:
                        if len(path_list)==0:
                            path_list=file_path_list
                            
                        t_dir=os.path.dirname(unicode(path_list[0]).rstrip("\\").rstrip("/"))
                        self.common_move(t_dir, path_list, a_is_in_history_add_datetime, a_is_in_history_add_version)

    
    #移动符合规则的文件
    def move_all_file_to_history(self, a_show_type, a_rule_view_list, a_is_in_history_add_datetime, a_is_in_history_add_version, a_path):
        #show_file_list为当前文件正在显示的文件列表
        t_show_file_list=[]
        t_dir=QDir(a_path)
        if a_show_type=="files":
            #显示文件
            t_dir.setNameFilters(ct_lib.com().change_to_file_rule_list(a_rule_view_list))
            #rule_list的规则是原先带有###的规则，需转换为??
            #设置过滤器(目录，文件或非上级目录)
            t_dir.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        else:
            a_rule_view_list.insert(0, "history")
            t_dir.setNameFilters(ct_lib.com().change_to_file_rule_list(a_rule_view_list))
            #rule_list的规则是原先带有###的规则，需转换为??
            #再过滤出文件，要规则过滤
            t_dir.setFilter(QDir.Dirs| QDir.Files| QDir.NoDotAndDotDot)
            
        info_list = t_dir.entryInfoList()
        for fileInfo in info_list:
            if ct_lib.com().is_match_regexp_list(a_rule_view_list, fileInfo.fileName()):
                t_show_file_list.append(fileInfo.absoluteFilePath())
        
            
        if len(t_show_file_list)>0:
            sou_list=[]
            for temp in t_show_file_list:
                if unicode(os.path.basename(temp)).strip().lower()!="history":
                    sou_list.append(temp)
            self.common_move(a_path, sou_list, a_is_in_history_add_datetime, a_is_in_history_add_version)
            
    #移动相同文件
    def move_same_file_to_history(self, a_drag_des_list, a_is_in_history_add_datetime, a_is_in_history_add_version, a_path):
        if len(a_drag_des_list)>0:
            sou_list=[]
            for drag_file in a_drag_des_list:
                if os.path.exists(drag_file):
                    sou_list.append(drag_file)
            self.common_move(a_path, sou_list, a_is_in_history_add_datetime, a_is_in_history_add_version)       
        
    
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
        t_is_move_same=unicode(t_argv.get_filebox_key("is_move_same")).strip().lower()
        t_is_in_history_add_datetime=unicode(t_argv.get_filebox_key("is_in_history_add_datetime")).strip().lower()
        t_is_in_history_add_version=unicode(t_argv.get_filebox_key("is_in_history_add_version")).strip().lower()
        try:
            t_tw = tw()
            #如果源和目标是同一个目录，不做移动
            if self.is_has_same_folder(t_sou_file_list, t_des_file_list):
                return self.ct_true()
            
            #取命名规则和路径
            filebox_info=self.get_filebox_info(t_tw, t_db, t_module, t_module_type, t_id_list[0], t_filebox_id)
            if filebox_info==False or not filebox_info.has_key("rule") or not filebox_info.has_key("path"):
                return self.ct_false("Get filebox info error")
            t_rule_view_list=filebox_info["rule_view"]
            t_path=filebox_info["path"]
            t_show_type=unicode(filebox_info["show_type"]).strip().lower()
            t_is_submit=unicode(filebox_info["is_submit"]).strip().lower()
            if not isinstance(t_rule_view_list, list):
                return self.ct_false("Get filebox rule error")	  
            
            #移动相同的文件
            if t_is_move_same=="y":
                self.move_same_file_to_history(t_des_file_list, t_is_in_history_add_datetime, t_is_in_history_add_version, t_path)
                return self.ct_true()

            
            if t_is_submit=="y":
                #如果是提交检查,移动上次提交的文件
                self.move_check_file_to_history(t_tw, t_db, t_module, t_module_type, t_id_list[0], t_is_in_history_add_datetime, t_is_in_history_add_version)
            else:
                #不是提交检查,移动符合命名规则的文件
                self.move_all_file_to_history(t_show_type, t_rule_view_list, t_is_in_history_add_datetime, t_is_in_history_add_version, t_path)
                
            return self.ct_true()
            
        except Exception,e:
            #print traceback.format_exc()
            return self.ct_false(e.message)
        
if __name__ == "__main__":
    #调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict=ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)


