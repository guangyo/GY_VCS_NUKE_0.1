#coding:utf-8
"""
  Author:  shiming
  Purpose: 禁止覆盖
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
        t_sou_list=t_argv.get_sys_file()
        t_des_list=t_argv.get_sys_des_file()
        t_no_same_folder_des_list=[]
        try:
            #取出不是源和目标相同目录的目标列表
            if len(t_sou_list)>=1 and len(t_des_list)>=1 and len(t_sou_list)==len(t_des_list):
                for i in range(len(t_sou_list)):
                    sou_dir=os.path.dirname(t_sou_list[i])
                    des_dir=os.path.dirname(t_des_list[i])
                    if sou_dir!=des_dir:
                        t_no_same_folder_des_list.append(t_des_list[i])
            #如果已经在的路径则报错
            error=""
            for path in t_no_same_folder_des_list:
                if os.path.exists(path):
                    if error=="":
                        error=path
                    else:
                        error=error+"\n"+path

            #最后要返回
            if error !="":
                return self.ct_false("File exist:"+"\n"+error)
            else:
                return self.ct_true()
            
        except Exception,e:
            #print traceback.format_exc()
            return self.ct_false(traceback.format_exc())
        
if __name__ == "__main__":
    #调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict=ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)
