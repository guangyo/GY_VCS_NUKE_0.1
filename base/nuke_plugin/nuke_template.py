# -*- coding: utf-8 -*-
#Author:王晨飞
#Time  :2017-1-2
#Describe:nuke模板
#         CgTeamWork_V5整理
import os
import sys
import json
import nuke
def nuke_template():
    t_template_file = sys.argv[1]
    t_des_file      = sys.argv[2]
    t_write_path    = sys.argv[3]
    t_source        = sys.argv[4]
    t_source_info   = json.loads( sys.argv[5] )
    try:
        nuke.scriptOpen( t_template_file.replace("\\","/") )
    except Exception,e:
        pass
    try:
        for t_node in nuke.allNodes():
            t_node_type  = t_node.Class()
            t_node_name  = t_node.name()
            if t_node_type == "Read":
                t_node["file"].setValue(t_source.replace("\\","/"))
                t_node["first"].setValue(1)
                t_node["last"].setValue(int(t_source_info["FrameCount"]))
                t_node["origfirst"].setValue(1)
                t_node["origlast"].setValue(int(t_source_info["FrameCount"]))            
            if t_node_type == "Write":
                t_node["file"].setValue( t_write_path.replace("\\","/") + "/" + os.path.basename(t_source.replace("\\","/")) )
        nuke.scriptSaveAs(filename=t_des_file.replace("\\","/"), overwrite=1)
    except Exception,e:
        pass
if __name__ == "__main__":
    nuke_template()