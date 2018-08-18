# -*- coding: utf-8 -*-
#Author:王晨飞
#Time  :2017-12-19
#Describe:maya通用方法
#         Shelf_Manage初始化更改,添加不存在就创建
#         CgTeamWork V5整合
import os
import sys
import maya
class Huds_Manage:
    def clear(self):
        try:
            T_All_Huds_List = maya.cmds.headsUpDisplay(lh=True, q=True)
            T_CG_Huds_List  = ["CG_1","CG_2","CG_3","CG_6","CG_7","CG_8"]
            for CG_Huds in T_CG_Huds_List:
                if CG_Huds in T_All_Huds_List:
                    maya.cmds.headsUpDisplay(CG_Huds,rem=True)
            return True
        except Exception,e:
            return False
    def delete(self, a_huds):
        try:
            T_All_Huds_List = maya.cmds.headsUpDisplay(lh=True, q=True)
            if a_huds in T_All_Huds_List:
                maya.cmds.headsUpDisplay(a_huds,rem=True)
                return True
            else:
                return False
        except Exception,e:
            return False
    def insert(self, a_huds, a_text):
        try:
            T_Huds_name = a_huds
            T_Huds_pos  = int(a_huds[3])
            T_Huds_text = a_text
            maya.cmds.headsUpDisplay(T_Huds_name,
                                     section=T_Huds_pos,
                                     block=2,
                                     labelWidth=50,
                                     labelFontSize="large",
                                     dataFontSize="large",
                                     dw=200, 
                                     l=T_Huds_text
                                     )
            return True
        except Exception,e:
            return False
class Camera_Manage:
    def setCameraAttr(self, a_attr, a_value):
        try:
            T_current_camera_object = self.currentCamera()
            if T_current_camera_object!=False:
                T_current_camera        = maya.cmds.listRelatives(T_current_camera_object ,s=1)
                maya.cmds.setAttr("%s.%s"%(T_current_camera[0], a_attr), a_value)
                return True
            else:
                return False
        except Exception,e:
            return False
    def currentCamera(self):
        try:
            T_current_view = maya.cmds.getPanel(vis=True)
            T_camera_views = maya.cmds.modelPanel(T_current_view[0], q=True, cam=True)
            if maya.cmds.objectType(T_camera_views, isAType='transform'):
                return T_camera_views
            else:
                transforms = maya.cmds.listRelatives(T_camera_views, parent=1)
                return transforms
        except Exception,e:
            return False
class DockControl_Manage:
    def __init__(self, a_window, a_object_name, a_dockcontrol_name):
        self.M_window           = a_window
        self.M_object_name      = a_object_name
        self.M_dockcontrol_name = a_dockcontrol_name
        self.M_win              = a_window()
    def show(self, a_position="right"):
        try:
            temp_window = maya.cmds.window(title='Layout')
            temp_column = maya.cmds.columnLayout()
            maya.cmds.layout(temp_column, query=True, height=True)
            maya.cmds.dockControl(self.M_dockcontrol_name+"_id",
                                  vis         = True,
                                  area        = a_position,
                                  l           = self.M_dockcontrol_name,
                                  content     = self.M_object_name,
                                  allowedArea = ["right","left"],
                                  w=500
                                  )
            return True
        except Exception,e:
            return False
    def close(self):
        try:
            maya.cmds.deleteUI(self.M_dockcontrol_name+"_id", control=True)
            return True
        except Exception,e:
            return False
    def isShow(self):
        try:
            return maya.cmds.dockControl(self.M_dockcontrol_name+"_id", vis=True, q=1)
        except Exception,e:
            return False
    def isExists(self):
        try:
            return maya.cmds.dockControl(self.M_dockcontrol_name+"_id", exists=True)
        except Exception,e:
            return False
class Shelf_Manage:
    def __init__(self, a_shelf_name):
        self.M_shelf_name = a_shelf_name
        if not cmds.shelfLayout(self.M_shelf_name, q=1, ex=1):
            gShelfTopLevel = mel.eval("global string $gShelfTopLevel;$tmp_1=$gShelfTopLevel;")
            cmds.shelfLayout(self.M_shelf_name, p=gShelfTopLevel)
    def getItems(self):
        try:
            return maya.cmds.shelfLayout(self.M_shelf_name, q=1, ca=1)
        except Exception,e:
            return []
    def getItemId(self, a_item):
        try:
            return maya.cmds.shelfButton(a_item, q=1, l=1)
        except Exception,e:
            return False
    def addItem(self, a_name, a_id, a_python_cmds):
        try:
            maya.cmds.shelfButton(commandRepeatable = True,
                                  width             = 35,
                                  height            = 35,
                                  image1            = "commandButton.png",
                                  command           = a_python_cmds,
                                  label             = a_id,
                                  parent            = self.M_shelf_name,
                                  sourceType        = "python",
                                  imageOverlayLabel = a_name,
                                  docTag            = a_id
                                  )
            return True
        except Exception,e:
            return False
    def deleteItem(self, a_item):
        try:
            maya.cmds.deleteUI(a_item, control=True)
            return True
        except Exception,e:
            return False

    