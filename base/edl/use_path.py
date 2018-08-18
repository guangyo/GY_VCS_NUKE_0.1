import os, sys
t_base_path      = os.path.dirname(os.path.dirname(__file__)).replace("\\","/")
t_icon_path      = t_base_path+"/com_icon"
t_pyside_path   = os.path.dirname(t_base_path) + "/lib/pyside"
t_ct_lib   = os.path.dirname(t_base_path) + "/cgtw"
if t_base_path not in sys.path:
    sys.path.append(t_base_path)
if t_pyside_path not in sys.path:
    sys.path.append(t_pyside_path)
if t_ct_lib not in sys.path:
    sys.path.append(t_ct_lib)   

def get_icon_path():
    t_base_path      = os.path.dirname(os.path.dirname(__file__)).replace("\\","/")
    return t_base_path+"/com_icon"    

def get_base_path():
    return os.path.dirname(os.path.dirname(__file__)).replace("\\","/")