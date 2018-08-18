#coding:utf-8
"""
  Author:  deming
  Purpose: 抄送
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
   
    #重写run,外部调用
    def run(self, a_dict_data):
        t_argv=ct_plu.argv(a_dict_data)
        t_db=t_argv.get_sys_database()
        t_module=t_argv.get_sys_module()
        t_module_type=t_argv.get_sys_module_type()
        t_id_list=t_argv.get_sys_id()
        t_des_file_path_list=t_argv.get_sys_des_file()
        t_account_id=t_argv.get_filebox_key("account_id")
        if not isinstance(t_account_id, (unicode,str)):
            return self.ct_true()
        t_account_id_list=unicode(t_account_id).split(",")
        
        if len(t_des_file_path_list)==0:
            return self.ct_false("There are no files drag in")
        try:
            t_tw = tw()
            content="submit:"
            for path in t_des_file_path_list:
                content=content+"<br>"+path            
            dic={"db":t_db, "module":t_module, "module_type":t_module_type, "task_id":t_id_list[0], "title":"", "content":content, "account_id_array":t_account_id_list}
            res=t_tw.con()._send("c_msg", "send_task", dic)           
            #最后要返回
            if res==True:
                return self.ct_true()
            else:
                return self.ct_false("Send msg to fail")
            
        except Exception,e:
            print traceback.format_exc()
            return self.ct_false(traceback.format_exc())
        



if __name__ == "__main__":
    #调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict=ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)
