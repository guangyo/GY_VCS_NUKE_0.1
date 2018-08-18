#coding:utf-8
"""
  Author:  shiming
  Purpose: 非制作人员禁止拖入
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
        
    def is_my_task(self, a_tw, a_db, a_module, a_module_type, a_task_id):
        t_account_id=a_tw.sys().get_account_id()
        dic={"db":a_db, "module":a_module, "module_type":a_module_type, "sign_filter_array": [ ["task.id","=",a_task_id],"and",["task.account_id","concat",t_account_id] ]}
        res=a_tw.con()._send("c_orm","get_count_with_filter", dic)
        if unicode(res).strip()!="":
            if int(res)>0:
                return True
        return False    
    
    #重写run,外部调用
    def run(self, a_dict_data):
        t_argv=ct_plu.argv(a_dict_data)
        t_db=t_argv.get_sys_database()
        t_module=t_argv.get_sys_module()
        t_module_type=t_argv.get_sys_module_type()
        t_id_list=t_argv.get_sys_id()
        
        t_check_group_id=t_argv.get_filebox_key("allow_group_id")
        try:
            t_tw = tw()
            #如果是我的任务不检查
            if self.is_my_task(t_tw, t_db, t_module, t_module_type, t_id_list[0]):
                return self.ct_true()
            
            #不是我的任务,但检查是否特别权限组执行
            t_res=t_tw.con()._send("c_group","is_in_group", {"check_group_id":t_check_group_id})
            #最后要返回
            if t_res==True:
                return self.ct_true()
            else:
                return self.ct_false("Unassigned, Can not drag in")
            
        except Exception,e:
            #print traceback.format_exc()
            return self.ct_false(e.message)
        
if __name__ == "__main__":
    #调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict=ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)
