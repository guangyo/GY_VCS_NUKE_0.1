# -*- coding: utf-8 -*-
import os
import sys
G_base_path = os.path.dirname( os.path.dirname( os.path.dirname( __file__.replace("\\","/") ) ) )

G_cgtw_path = os.path.dirname( G_base_path ) + "/cgtw/"
G_lib_outside_path = os.path.dirname( G_base_path ) + "/lib/outside"
G_lib_pyside_path = os.path.dirname( G_base_path ) + "/lib/pyside"
G_com_path  = G_base_path + "/com_lib/"

if not G_base_path in sys.path:
    sys.path.append( G_base_path )
if not G_cgtw_path in sys.path:
    sys.path.append( G_cgtw_path )

if not G_lib_outside_path in sys.path:
    sys.path.append( G_lib_outside_path )
    
if not G_lib_pyside_path in sys.path:
    sys.path.append( G_lib_pyside_path )        

if not G_com_path in sys.path:
    sys.path.append( G_com_path )

def sys_connect(a_signal, a_slot):
    try:
        print a_slot
        a_signal.connect(a_slot)
    except Exception,e:
        print e.message