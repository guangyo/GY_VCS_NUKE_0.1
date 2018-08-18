#coding:utf-8
"""
  Author:  deming
  Purpose: 任务完成拖入不提交检查
  Created: 2018-03-15
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
        
    def is_task_finish(self, a_tw, a_db, a_module, a_module_type, a_task_id):
        #当前的阶段是否完成了
        dic={"db":a_db, "module":a_module, "module_type":a_module_type, "sign_filter_array": [ ["task.id","=",a_task_id],"and",["task.flow_finish_id","=","1"] ]}
        t_res=a_tw.con()._send("c_orm","get_count_with_filter", dic)
        if unicode(t_res).strip()!="":
            if int(t_res)>0:
                return True
        return False      
    
    #重写run,外部调用
    def run(self, a_dict_data):
        t_argv=ct_plu.argv(a_dict_data)
        t_db=t_argv.get_sys_database()
        t_module=t_argv.get_sys_module()
        t_module_type=t_argv.get_sys_module_type()
        t_id_list=t_argv.get_sys_id()
        try:
            t_tw = tw()
            #判断任务是否完成
            if self.is_task_finish(t_tw, t_db, t_module, t_module_type, t_id_list[0]):
                return self.ct_true({"is_can_submit":"N"})
            return self.ct_true({"is_can_submit":"Y"})
            
        except Exception,e:
            print traceback.format_exc()
            return self.ct_false(traceback.format_exc())

if __name__ == "__main__":
    #调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict=ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)
