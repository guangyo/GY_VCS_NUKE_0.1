#coding:utf-8
"""
  Author:  shiming
  Purpose: 检查允许拖入权限组
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
    
    #重写run,外部调用
    def run(self, a_dict_data):
        t_argv=ct_plu.argv(a_dict_data)
        t_check_group_id=t_argv.get_filebox_key("allow_group_id")
        try:
            t_tw = tw()
            t_res=t_tw.con()._send("c_group","is_in_group", {"check_group_id":t_check_group_id})
            #最后要返回
            if t_res==True:
                return self.ct_true()
            else:
                return self.ct_false("No Permission to drag in")
            
        except Exception,e:
            #print traceback.format_exc()
            return self.ct_false(traceback.format_exc())
        
if __name__ == "__main__":
    #调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict=ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)
