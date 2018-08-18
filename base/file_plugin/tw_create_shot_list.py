# -*- coding: utf-8 -*-
"""
    Author:    黄骁颖
    Purpose:   create_shot_list
    Created:   2018-04-19
"""

import os
import re
import sys
import time
import json
import shutil
import datetime
import traceback
G_base_path = os.path.dirname( os.path.dirname( __file__.replace("\\","/") ) )
G_com_path  = G_base_path + "/com_lib/"
G_cgtw_path = os.path.dirname( G_base_path ) + "/cgtw/"
if not G_base_path in sys.path:
    sys.path.append( G_base_path )
if not G_com_path in sys.path:
    sys.path.append( G_com_path ) 
if not G_cgtw_path in sys.path:
    sys.path.append( G_cgtw_path )
import ct

from   com_message_box import *
from   cgtw            import *
from   com_function    import * 
from   com_widget      import *

#早期的打包出去中没有exifread库
G_exist_exifread=True
try:
    t_exifread_path=os.path.dirname( G_base_path ) + "/lib/inside/exifread2"
    if not t_exifread_path in sys.path:
        sys.path.append( t_exifread_path )
    import exifread
except Exception,e:
    G_exist_exifread=False
    

class create_shot_widget(widget):
    m_col_filename       = 0
    m_col_shot           = 1
    m_col_frame          = 2
    m_col_fps            = 3
    m_col_resolution     = 4
    m_col_start_timecode = 5
    m_col_end_timecode   = 6
    m_col_status         = 7
    
    #放在userrole中的值
    m_role_path           = 32#路径,比如如果是文件夹的话,路径为:z:/aa, role_file_path则是z:/aa/xx.jpg    如果是文件的话m_role_path和m_role_file_path_list是一样的
    m_role_file_path_list = 33#完整路径    
    m_role_tooltip        = 34#点击提示信息
     
    m_Thread_runing = False
    def __init__(self):
        super(create_shot_widget, self).__init__()
        self.__ui__()
        self.set_Cgtw()
        self.init_argv()
    def set_Cgtw(self):
        try:
            self.m_tw = tw()
            self.m_database = self.m_tw.sys().get_sys_database()
            self.k_action   = self.m_tw.sys().get_argv_key("action")
            t_eps_class     = self.m_tw.info_module(self.m_database, "eps")
            t_eps_class.init_with_filter([["eps.eps_name","has","%"]] )
            self.m_eps_data = t_eps_class.get(["eps.eps_name"])
        except Exception,e:
            message().error(u"读取数据库失败")
        if self.k_action == "image":
            self.m_title = u"拖入图片生成镜头信息"
        elif self.k_action == "mov":
            self.m_title = u"拖入mov生成镜头信息"
        else:
            message().error(u"插件参数配置错误!")
        self.set_UI()
        self.show()


    def set_UI(self):
        self.setMinimumSize(600,400)
        self.m_title_label.setText(self.m_title)
        
        col_list=[u"文件名",u"镜头号",u"帧数", u"帧率", u"分辨率", u"开始时间码", u"结束时间码",u"状态"]
        self.m_tablewidget = QTableWidget()
        self.m_tablewidget.setRowCount(0)
        self.m_tablewidget.setColumnCount(len(col_list) )      
        self.m_tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.m_tablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.m_tablewidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.m_tablewidget.setSelectionMode(QAbstractItemView.ExtendedSelection)      
        self.m_tablewidget.verticalHeader().setVisible(False)
        self.m_tablewidget.setHorizontalHeaderLabels(col_list)
        self.m_tablewidget.setAcceptDrops(True)
        self.m_tablewidget.dropEvent=self.dropEvent
        self.m_tablewidget.dragEnterEvent=self.dragEnterEvent
        self.m_tablewidget.dragMoveEvent=self.dragMoveEvent        
        self.parent_lay.addWidget(self.m_tablewidget)
        self.m_tablewidget.itemClicked.connect(self.slt_show_tooltip)
        #---
        self.m_tablewidget.setContextMenuPolicy(Qt.CustomContextMenu)#右键菜单
        self.m_tablewidget.customContextMenuRequested.connect(self.slt_CustomContextMenu)

        
        #---
        self.m_combobox_text= QLabel()
        self.m_combobox_text.setText(u"集数/场次")
        self.m_combobox_eps = QComboBox()
        self.m_delete_button= QPushButton()
        self.m_delete_button.setText(u"删除")
        self.m_delete_button.clicked.connect( self.slt_delete )
        self.m_ok_button    = QPushButton()
        self.m_ok_button.setText(u"确定")
        self.m_ok_button.clicked.connect( self.slt_ok )
        lay_bottom = QHBoxLayout()
        lay_bottom.setContentsMargins(0,8,0,0)
        lay_bottom.addWidget(self.m_combobox_text)
        lay_bottom.addWidget(self.m_combobox_eps)
        lay_bottom.addStretch()
        lay_bottom.addWidget(self.m_delete_button)
        lay_bottom.addSpacing(8)
        lay_bottom.addWidget(self.m_ok_button)
        self.parent_lay.addLayout(lay_bottom)
        self.m_close_button.clicked.connect(self.slt_close)
        
        self.set_Style()
        try:
            if type(self.m_eps_data) == list:
                for data in self.m_eps_data:
                    self.m_combobox_eps.addItem( data["eps.eps_name"], data['id'])
        except:
            message().error(u"获取集数失败!")
    
    def slt_show_tooltip(self,a_item): #点击提示tooltip
        t_row          = self.m_tablewidget.row(a_item)
        t_tooltip_data = self.m_tablewidget.item(int(t_row), self.m_col_status).data(self.m_role_tooltip)
        QToolTip.showText(QCursor.pos(), t_tooltip_data)
        


        
        
    def slt_CustomContextMenu(self):#右键菜单
        QMenu_popMenu = QMenu(self)
        Qaction_up    = QAction(u"重新提交",self)  
        item4         = QMenu_popMenu.addAction(Qaction_up)
        a_action      = QMenu_popMenu.exec_(QCursor.pos())
  
        if a_action == Qaction_up:
            if self.m_Thread_runing == True:
                message().error(u"请等待上传",False)
            else:
                self.memu_upload_again()
    def memu_upload_again(self): #右键重新上传
        row_list = []
        t_list   = self.m_tablewidget.selectedItems()
        for item in t_list:
            row = item.row()
            if row_list.count(row)==0:
                row_list.append(row)
        row_list.sort()
        t_count = len(row_list)

    
        t_data_list = self.get_task_data(row_list,again=True)
        if t_data_list == []:
            message().error(u"不存在需要重新上传的镜头",False)
            return
        try:
            self.thread_work = thread_work(t_data_list, self.t_key_dict)
            self.thread_work.sig_status.connect(self.send_status_data)
            self.thread_work.sig_thread_status.connect(self.slt_thread_status)
            self.thread_work.sig_return_row_status.connect(self.slt_updata_row)
            self.thread_work.start()                        
        except Exception,e:
            pass

        
    def set_Style(self):
        self.m_combobox_text.setFixedSize(60,28)
        self.m_combobox_text.setStyleSheet("QLabel{color:#666666;font-size:12px;}")
        self.m_tablewidget.setStyleSheet("QTableWidget{font-size:12px;color:#666666;border:1px solid #E5E6E7;border-radius:4px;outline:none;}"
                                         "QHeaderView::section{background:red;color:#666666;outline:none;}"
                                         "QHeaderView{min-height:32px;outline:none;}")
        self.m_combobox_eps.setView(QListView())
        self.m_combobox_eps.setFixedSize(180,28)
        self.m_combobox_eps.setStyleSheet("QComboBox{background-color:#FFFFFF;border:1px solid #E5E6E7; border-radius:4px;font-size:12px;color:#666666;}"
                                          "QListView{background-color: #FFFFFF;height:50px;outline:none;}"
                                          "QListView::Item{height:28px;font-size:12px;color:#666666;outline:none;}"
                                          "QListView::Item:hover{background-color:#E9E9E9;outline:none;}"
                                          "QListView::Item:selected{background-color:#E9E9E9;outline:none;}"
                                          "QComboBox::down-arrow {image: url(" + self.m_icon_path + "/com_icon/down-arrow.png);}"
                                          "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width:28px;border:none;}"
                                          )         
        self.m_ok_button.setFixedSize(60,28)
        self.m_ok_button.setStyleSheet("QPushButton{background-color:#108ee9;color:#FFFFFF;font-size:12px;border-radius:4px;}"
                                       "QPushButton:hover{background-color:#1083E0; border-radius:4px; font-size:12px; color:#FFFFFF;}"
                                       )
        self.m_delete_button.setFixedSize(60,28)
        self.m_delete_button.setStyleSheet("QPushButton{background-color:#FFFFFF;color:#666666;font-size:12px;border-radius:4px;border:1px solid #999999;}"
                                           "QPushButton:hover{background-color:#FFFFFF; border-radius:4px; font-size:12px; color:#0F87DE;border:1px solid #0F87DE}"
                                           )

    #----------------------------------------call------------------------------------
    def init_argv(self):
        self.K_shot_string_rule             = self.m_tw.sys().get_argv_key("shot_string_rule")          #镜头号规则
        self.K_file_format                  = self.m_tw.sys().get_argv_key("file_format")               #允许格式(用于序列)  ,key可空
        self.k_is_get_thumbnail             = self.m_tw.sys().get_argv_key("is_get_thumbnail")          #是否获取缩略图   key可空
        self.k_last_frame_thumbnail_field   = self.m_tw.sys().get_argv_key("last_frame_thumbnail_field")#最后一帧缩略图   ,key可空
        self.k_des_file_sign                = self.m_tw.sys().get_argv_key("des_file_sign")             #目标文件标识(拷贝)  ,key可空
        self.K_source_field                 = self.m_tw.sys().get_argv_key("source_field")              #添加到素材字段   ,key可空
        self.K_resolution_field             = self.m_tw.sys().get_argv_key("resolution_field")              #分辨率字段   ,key可空
        self.K_fps_field                    = self.m_tw.sys().get_argv_key("fps_field")              #帧率字段(用于mov)   ,key可空
        self.K_start_timecode_field         = self.m_tw.sys().get_argv_key("start_timecode_field")              #开始时间码字段(用于序列)   ,key可空
        self.K_end_timecode_field           = self.m_tw.sys().get_argv_key("end_timecode_field")              #结束时间码字段(用于序列)   ,key可空
        if unicode(self.K_resolution_field) =="" or self.K_resolution_field==False:
            self.m_tablewidget.setColumnHidden(self.m_col_resolution, True)
        
        if unicode(self.K_fps_field)=="" or self.K_fps_field==False:
            self.m_tablewidget.setColumnHidden(self.m_col_fps, True)
        
        self.m_is_has_timecode=False
        if unicode(self.K_start_timecode_field)=="" or self.K_start_timecode_field==False:
            self.m_tablewidget.setColumnHidden(self.m_col_start_timecode, True)
        else:
            self.m_is_has_timecode=True
        
        if unicode(self.K_end_timecode_field)=="" or self.K_end_timecode_field==False:
            self.m_tablewidget.setColumnHidden(self.m_col_end_timecode, True)
        else:
            self.m_is_has_timecode=True
        #判断exifread库是否存在,早期的库是没有一起打包出去的
        if self.m_is_has_timecode and not G_exist_exifread:
            t_path=os.path.dirname( G_base_path ) + "/lib/inside/exifread"
            message().error(u"exifread库不存在("+t_path+")", True )
                

        

   
   
    def send_status_data(self, a_row, a_status, t_tooltip_data): #改变状态栏 ,tootip
        if a_status == u"ok":
           
            self.m_tablewidget.setItem(int(a_row), self.m_col_status, QTableWidgetItem(u"success"))
            self.m_tablewidget.item(int(a_row), self.m_col_status).setData(self.m_role_tooltip,t_tooltip_data)
            self.m_tablewidget.item(int(a_row), self.m_col_status).setToolTip(t_tooltip_data)
            
            
        elif a_status == u"error":
            t_item =  QTableWidgetItem(u"error")
            t_item.setBackground(Qt.red)
            self.m_tablewidget.setItem(int(a_row),self.m_col_status,t_item )
            self.m_tablewidget.item(int(a_row), self.m_col_status).setToolTip(t_tooltip_data)
            self.m_tablewidget.item(int(a_row), self.m_col_status).setData(self.m_role_tooltip,t_tooltip_data)
            
            self.m_tablewidget.sortItems(self.m_col_status)
            
        elif a_status == u"完成" :
            all_status_success =True #判断列表中是否全部上传成功
            for i in range(self.m_tablewidget.rowCount()):
                if  self.m_tablewidget.item(i, self.m_col_status).text() != "success":
                    all_status_success = False
            if all_status_success == True:
                message().info(u"完成")
            else:
                message().info(u"完成",False)

        elif a_status == (u"有错"):
            message().error(u"上传有错，请查看状态列",False)

    def check_exist_error(self,row_list,again):#检查是否存在错误
        if again == True: #如果是右键选中重新上传
            t_count = len(row_list)
        else:
            t_count = row_list
            
        for i in range(t_count):
            if again == True:  #如果是右键选中重新上传
                i = row_list[t_count-i-1]        
        
            try:
                t_combobox  = self.m_tablewidget.cellWidget(i, self.m_col_shot)
                t_shot_name = t_combobox.currentText()
                if t_shot_name == "":
                    return False
            except:
                return False
        return True    
    def get_shot_name(self, a_name):#用规则取镜头号
        if self.K_shot_string_rule==False:
            t_rule = "*"
        else:
            t_rule = self.K_shot_string_rule
        return com_rule_to_str(a_name, com_str_to_rule(unicode(t_rule)))
    
    def get_timecode(self, a_path):#取时间码
        try:
            FIELD = 'EXIF DateTimeOriginal'
            fd = open(a_path, 'rb')
            tags = exifread.process_file(fd)
            fd.close()
            if FIELD in tags:
                return str(tags[FIELD]).replace(":","").replace(" ","")            
        except Exception,e:
            fd.close()
            traceback.print_exc()
            return ""
              
    
    def get_file_info_dict(self, a_path):#取文件信息
        t_resolution     = "0x0"
        t_start_timecode = ""
        t_end_timecode   = ""
        if self.k_action == "image":#表示是序列,同时取出符合图片的规则
            t_file_list = []
            try:
                if self.K_file_format == False:
                    t_temp_list = ct.file().get_path_list(unicode(a_path))
                else:
                    t_temp_list = ct.file().get_path_list(unicode(a_path),unicode(self.K_file_format).split("|"))
                for i in t_temp_list:
                    if not str(i).lower().strip().split(".")[-1] in [ 'ini', "db"]:
                        t_file_list.append( com_replace_path(i) )
                
                if len(t_file_list)>0:
                    t_dict=ct.mov().get_size(t_file_list[0], False)#取分辨率
                    t_resolution=t_dict["Width"]+"x"+t_dict["Heigh"]
                
            except Exception,e:
                pass
            
            #取开始时间码
            if self.m_is_has_timecode:
                try:
                    if len(t_file_list)>0:
                        t_start_timecode=self.get_timecode(t_file_list[0])#开始时间码
                        t_end_timecode=self.get_timecode(t_file_list[-1])#结束时间码
                except Exception,e:
                    traceback.print_exc()
                    pass               
            
            return {"frame":unicode(len(t_file_list)), "path_list":t_file_list, "fps":"0" ,"resolution":t_resolution, "start_timecode":t_start_timecode, "end_timecode":t_end_timecode}
        else:#表示是mov
            t_frame = "0"
            t_fps   = "0"
            try:
                t_data = ct.mov().get_avi_info( a_path )
                t_frame=t_data["FrameCount"]
                t_fps=t_data["FrameRate"]
            except Exception,e:
                traceback.print_exc()
                pass  
            
            try:
                t_dict=ct.mov().get_size(a_path)#取分辨率
                t_resolution = t_resolution=t_dict["Width"]+"x"+t_dict["Heigh"]
            except Exception,e:
                traceback.print_exc()
                pass              
            return {"frame":t_frame, "path_list": [com_replace_path(a_path)], "fps": t_fps, "resolution":t_resolution, "start_timecode":"", "end_timecode":""} 

    #----------------------------------------slot------------------------------------
    def slt_ok(self):
        
        t_data_list = self.get_task_data(self.m_tablewidget.rowCount())

        if t_data_list == []:
            message().error(u"请拖入文件",False)
            self.m_ok_button.setEnabled(True)
            return 
        try:
            self.thread_work = thread_work(t_data_list, self.t_key_dict)
            self.thread_work.sig_status.connect(self.send_status_data)
            self.thread_work.sig_thread_status.connect(self.slt_thread_status)
            self.thread_work.sig_return_row_status.connect(self.slt_updata_row)
            self.thread_work.start()            
        except Exception,e:
            pass
        

    
    def slt_updata_row(self,a_row): #改变行的选中状态    
        self.m_tablewidget.setCurrentItem(self.m_tablewidget.item(a_row, 0))
        
    def slt_thread_status(self,status):#判断是否正在执行上传
        if status == "work":
            self.m_Thread_runing = True
        else:
            self.m_Thread_runing =False
            self.m_ok_button.setEnabled(True)
        
    def get_task_data(self, row_list, again = False ):
        if not self.check_exist_error(row_list,again):
            message().error(u"存在空的镜头号,请检查!",False)
            return
        self.m_ok_button.setEnabled(False)
        try:
            t_class_shot  = self.m_tw.info_module(self.m_database,"shot")
            t_eps_id      = self.m_combobox_eps.itemData(self.m_combobox_eps.currentIndex())
            t_eps         = unicode(self.m_combobox_eps.currentText())
        except:
            message().error(u"初始化失败!",False)
            return
        
        if again == True: #如果是右键选中重新上传
            t_count = len(row_list)
        else:
            t_count = row_list
        
        t_data_list  = []
        for i in range(t_count):
            if again == True:  #如果是右键选中重新上传
                i = row_list[t_count-i-1]
                
            self.m_tablewidget.setItem(i, self.m_col_status, QTableWidgetItem(u"wait"))
            t_combobox       = self.m_tablewidget.cellWidget(i, self.m_col_shot)
            t_shot_name      = t_combobox.currentText()
            t_frame          = unicode( self.m_tablewidget.item(i, self.m_col_frame).text() )   
            t_file_path_list = self.m_tablewidget.item(i, self.m_col_filename).data(self.m_role_file_path_list)
            t_path           = self.m_tablewidget.item(i, self.m_col_filename).data(self.m_role_path)
            t_fps            = self.m_tablewidget.item(i, self.m_col_fps).text()   
            t_resolution     = self.m_tablewidget.item(i, self.m_col_resolution).text()
            t_start_timecode = self.m_tablewidget.item(i, self.m_col_start_timecode).text()
            t_end_timecode   = self.m_tablewidget.item(i, self.m_col_end_timecode).text()
    
            self.t_key_dict = {"K_source_field":self.K_source_field,"k_action":self.k_action,"K_fps_field":self.K_fps_field,"K_resolution_field":self.K_resolution_field,"K_start_timecode_field":self.K_start_timecode_field,"K_end_timecode_field":self.K_end_timecode_field,"k_is_get_thumbnail":self.k_is_get_thumbnail,"k_last_frame_thumbnail_field":self.k_last_frame_thumbnail_field,"k_des_file_sign":self.k_des_file_sign}
    
            t_data_list.append({"row":i,"shot": t_shot_name, "frame": t_frame, "file_path_list": t_file_path_list,
                                    "path":t_path, "class_shot":t_class_shot, "eps_id":t_eps_id, "eps":t_eps,
                                    "fps":t_fps, "resolution":t_resolution, "start_timecode":t_start_timecode, "end_timecode":t_end_timecode})
            
            
        return t_data_list
        
    def slt_delete(self):
        row_list = []
        t_list=self.m_tablewidget.selectedItems()
        for item in t_list:
            row=item.row()
            if row_list.count(row)==0:
                row_list.append(row)
        row_list.sort()
        t_count=len(row_list)
        for i in range(t_count):
            self.m_tablewidget.removeRow(row_list[t_count-i-1])           
    def slt_close(self):
        sys.exit()
    def init_drag_info(self, a_path_list):
        t_combobox_style='''
        QComboBox{background-color:transparent;border:0px;font-size:12px;color:#666666;}
        QListView{background-color: #FFFFFF;height:50px;outline:none;}
        QListView::Item{height:28px;font-size:12px;color:#666666;outline:none;}
        QListView::Item:hover{background-color:#E9E9E9;outline:none;}
        QListView::Item:selected{background-color:#E9E9E9;outline:none;}
        QComboBox::down-arrow {image: url(" + self.m_icon_path + "/com_icon/down-arrow.png);}
        QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width:28px;border:none;}
        '''
        
        t_fail = []
        for t_path in a_path_list :
            try:
                t_path       = com_replace_path( t_path )
                t_filename=os.path.basename(t_path)
                t_row = self.m_tablewidget.rowCount()
                self.m_tablewidget.insertRow( t_row )
                self.m_tablewidget.setRowHeight(t_row, 28)
                
                self.m_tablewidget.setItem(t_row, self.m_col_filename, QTableWidgetItem( t_filename ) )
                self.m_tablewidget.item(t_row, self.m_col_filename).setData(self.m_role_path, t_path)

                file_info_dict    = self.get_file_info_dict( t_path )#返回帧数和帧率和分辨率和完整路径列表

                self.m_tablewidget.setItem(t_row, self.m_col_frame, QTableWidgetItem(file_info_dict["frame"]) )
                self.m_tablewidget.item(t_row, self.m_col_filename).setData(self.m_role_file_path_list, file_info_dict["path_list"])  #保存完整路径
                self.m_tablewidget.setItem(t_row, self.m_col_fps,            QTableWidgetItem(file_info_dict["fps"]) )#帧率
                self.m_tablewidget.setItem(t_row, self.m_col_resolution,     QTableWidgetItem(file_info_dict["resolution"]) )#分辨率
                self.m_tablewidget.setItem(t_row, self.m_col_end_timecode,   QTableWidgetItem(file_info_dict["end_timecode"]) )#结束时间码
                self.m_tablewidget.setItem(t_row, self.m_col_start_timecode, QTableWidgetItem(file_info_dict["start_timecode"]) )#开始时间码
                self.m_tablewidget.setItem(t_row, self.m_col_status,         QTableWidgetItem(u"wait"))
                #生成combobox控件放到表格中
                
                
                t_shot_name_list = self.get_shot_name(  os.path.splitext(t_filename)[0] )
                shot_name_combobox = QComboBox()
                shot_name_combobox.setView(QListView())
                shot_name_combobox.setStyleSheet(t_combobox_style)  
                shot_name_combobox.setFixedHeight(28)
                for t_shot_name in t_shot_name_list:
                    shot_name_combobox.addItem(t_shot_name)
                self.m_tablewidget.setCellWidget(t_row, self.m_col_shot, shot_name_combobox)
                
                
                #---拖入后
                if t_shot_name_list == [] or str(file_info_dict["frame"]) == str(0)  :
                    t_item =  QTableWidgetItem(u"error")
                    t_item.setBackground(Qt.red)                    
                    self.m_tablewidget.setItem(t_row, self.m_col_status, t_item)                
                    self.m_tablewidget.item(t_row, self.m_col_status).setData(self.m_role_tooltip,'<span style="color:#FF0000;">'+ u"镜头为空或帧数错误\n"+'</span>')
                
            except:
                traceback.print_exc()
                t_fail.append( t_path )
                
                
                
        if t_fail!=[]:

            message().error(u"以下文件拖入后获取数据失败:\n" + unicode( "\n".join(t_fail) ), False )
    #----------------------------------------event------------------------------------
    def dropEvent(self,e):
        t_all_list = []
        mime =e.mimeData()
        if mime.hasUrls():
            for i in range(len(mime.urls())):
                t_path=mime.urls()[i].toLocalFile()
                if self.k_action == "image":
                    if os.path.isdir( t_path ):
                        t_all_list.append( t_path )
                else:
                    if os.path.isfile( t_path ):
                        t_all_list.append( t_path )
        self.init_drag_info( t_all_list )
    def dragEnterEvent(self,e):
        e.accept()
    def dragMoveEvent(self,e):
        e.acceptProposedAction()

class thread_work(QThread):
    sig_status            = Signal(int,str,str)
    sig_thread_status     = Signal(str)
    sig_return_row_status = Signal(int)
    def __init__(self,a_data_list,a_key_dict):
        super(thread_work,self).__init__()    
        
        self.a_data_list                  = a_data_list
        self.K_fps_field                  = a_key_dict["K_fps_field"]
        self.K_resolution_field           = a_key_dict["K_resolution_field"]
        self.K_start_timecode_field       = a_key_dict["K_start_timecode_field"]
        self.K_end_timecode_field         = a_key_dict["K_end_timecode_field"]
        self.k_is_get_thumbnail           = a_key_dict["k_is_get_thumbnail"]
        self.k_last_frame_thumbnail_field = a_key_dict["k_last_frame_thumbnail_field"]
        self.k_des_file_sign              = a_key_dict["k_des_file_sign"]
        self.k_action                     = a_key_dict["k_action"]
        self.K_source_field               =  a_key_dict["K_source_field"]
    def run(self):
        self.sig_thread_status.emit("work")
        self.do()
        
    def do(self):
        t_create_shot_fail           = []
        t_update_frame_fail          = []
        t_update_fps_fail            = []
        t_update_resolution_fail     = []
        t_update_pix_fail            = []
        t_update_last_fail           = []
        t_copy_file_fail             = []
        t_update_source_fail         = []    
        t_update_start_timecode_fail = []    
        t_update_end_timecode_fail   = []    
        t_check_shot_fail            = []
        t_init_shot_fail             = []    
    
        for data_dict  in  self.a_data_list:
            self.t_status  = True #是否失败
            t_tooltip_data = ""   #新提示信息

            t_row            = data_dict["row"]
            
            t_shot_name      = data_dict["shot"]
            t_frame          = data_dict["frame"]
            t_file_path_list = data_dict["file_path_list"]#完整路径列表
            t_path           = data_dict["path"]
            t_class_shot     = data_dict["class_shot"]
            t_eps_id         = data_dict["eps_id"]
            t_eps            = data_dict["eps"]
            t_fps            = data_dict["fps"]
            t_resolution     = data_dict["resolution"]
            t_start_timecode = data_dict["start_timecode"]
            t_end_timecode   = data_dict["end_timecode"]
    
            self.sig_return_row_status.emit(t_row)
            
            t_tooltip_data += '<span >'+ u"Info:获取缩略图:---->%s\n"%(t_shot_name)+ '</span>'
            try:
                t_image_dict = self.get_image_dict(t_file_path_list)
            except Exception,e:
                t_tooltip_data += '<br><span style="color:#FF0000;">'+  u"Error:生成本地缩略图:---->%s\n"%(e.message) + '</span>'
                self.sig_status.emit(t_row, "error", t_tooltip_data)
                t_check_shot_fail.append(t_shot_name)
                continue    
    
            
            try:
                t_tooltip_data +=  '<br><span >'+  u"Info:检查镜头号:---->%s\n"%(t_shot_name)+ '</span>'
                res = t_class_shot.init_with_filter([[u"eps.eps_name","=",t_eps],"and",[u"shot.shot","=",t_shot_name]])
            except Exception,e:
                t_tooltip_data += '<br><span style="color:#FF0000;">'+  u"Error:检查镜头号失败:---->%s\n"%(t_shot_name) + '</span>'
                self.sig_status.emit(t_row, "error", t_tooltip_data)
                t_check_shot_fail.append(t_shot_name)
                continue
    
            if len(t_class_shot.get_id_list())==0:
                try:
                    t_res = t_class_shot.create({"shot.shot":t_shot_name,"eps.id":t_eps_id})
                    t_tooltip_data +=  '<br><span >'+ u"Info:创建镜头号:------>%s\n"%(t_shot_name)+ '</span>'
    
                except Exception,e:
                    t_tooltip_data += '<br><span style="color:#FF0000;">'+ u"Error:创建镜头号失败:------>%s\n"%(t_shot_name)+ '</span>'
                    self.sig_status.emit(t_row, "error", t_tooltip_data)
                    continue
    
                if t_res==False:
                    t_create_shot_fail.append( t_shot_name )
                    t_tooltip_data += '<br><span style="color:#FF0000;">'+ u"Error:创建镜头号失败:------>%s\n"%(t_shot_name)+ '</span>'
                    self.sig_status.emit(t_row, "error", t_tooltip_data)      
                    continue
                else:
                    try:
                        t_tooltip_data +=  '<br><span >'+ u"Info:初始化镜头号:---->%s\n"%(t_shot_name)+ '</span>'
                        t_class_shot.init_with_filter([[u"eps.eps_name",u"=",t_eps],"and",[u"shot.shot",u"=",t_shot_name]])
    
                    except Exception,e:
                        t_tooltip_data += '<br><span style="color:#FF0000;">'+ u"Error:初始化镜头号失败:---->%s\n"%(t_shot_name)+ '</span>'
                        self.sig_status.emit(t_row, "error", t_tooltip_data)    
                        t_init_shot_fail.append(t_shot_name)
                        continue
    
    
            #更新帧数
            try:
                t_tooltip_data +=  '<br><span >'+ u"Info:更新帧数:---->%s\n"%(t_shot_name)+ '</span>'
                update_frame = t_class_shot.set({"shot.frame":t_frame})
                if update_frame==False:
                    t_update_frame_fail.append( t_shot_name+":"+t_frame )
                    t_tooltip_data +=  '<br><span style="color:#FF0000;">'+ u"Error:更新帧数失败:---->%s\n"%(t_shot_name) + '</span>'
                    self.t_status = False
            except Exception,e:  
                t_tooltip_data +=   '<br><span style="color:#FF0000;">'+ u"Error:更新帧数失败:---->%s\n"%(t_shot_name)+ '</span>'
                self.t_status = False
    
            #更新帧率
            if str( self.K_fps_field ).lower().strip()!="" and self.K_fps_field!=False:
                try:
                    t_tooltip_data +=  '<br><span >'+   u"Info:更新帧率:---->%s\n"%(t_shot_name)+ '</span>'
    
                    update_fps = t_class_shot.set({self.K_fps_field:t_fps})
        
                    
                    if update_fps==False:
                        t_update_fps_fail.append( t_shot_name+":"+t_fps )
                        t_tooltip_data += '<br><span style="color:#FF0000;">'+   u"Error:更新帧率失败:---->%s\n"%(t_shot_name)+ '</span>'
                        self.t_status = False
                except Exception,e:
                    t_tooltip_data +=  '<br><span style="color:#FF0000;">'+  u"Error:更新帧率失败:---->%s\n"%(t_shot_name)+ '</span>'
                    self.t_status = False
    
            #更新分辨率
            if str( self.K_resolution_field ).lower().strip()!="" and self.K_resolution_field!=False:
                try:
                    t_tooltip_data +=  '<br><span >'+  u"Info:更新分辨率:---->%s\n"%(t_shot_name)+ '</span>'
    
                    update_resolution = t_class_shot.set({self.K_resolution_field:t_resolution})
      
                    
                    
                    if update_resolution==False:
                        t_update_resolution_fail.append( t_shot_name+":"+t_resolution )
                        t_tooltip_data +=   '<br><span style="color:#FF0000;">'+  u"Error:更新分辨率失败:---->%s\n"%(t_shot_name)+ '</span>'
                        self.t_status = False
    
                except Exception,e:
                    t_tooltip_data +=   '<br><span style="color:#FF0000;">'+  u"Error:更新分辨率失败:---->%s\n"%(t_shot_name)+ '</span>'
                    self.t_status = False
    
            #更新开始时间码
            if str( self.K_start_timecode_field ).lower().strip()!="" and self.K_start_timecode_field!=False:
                try:
                    t_tooltip_data +=    '<br><span >'+   u"Info:更新开始时间码:---->%s\n"%(t_shot_name)+ '</span>'
                    update_start_timecode = t_class_shot.set({self.K_start_timecode_field:t_start_timecode})
                    print u"更新开始时间码:",update_start_timecode,"t_start_timecode:",t_start_timecode
                    
                    if update_start_timecode==False:
                        t_update_start_timecode_fail.append( t_shot_name+":"+t_start_timecode )
                        t_tooltip_data +=   '<br><span style="color:#FF0000;">'+  u"Error:更新开始时间码失败:---->%s\n"%(t_shot_name) + '</span>' 
                        self.t_status = False
                except Exception,e:
                    t_tooltip_data +=  '<br><span style="color:#FF0000;">'+   u"Error:更新开始时间码失败:---->%s\n"%(t_shot_name)  + '</span>'
                    self.t_status = False
    
            #更新结束时间码
            if str( self.K_end_timecode_field ).lower().strip()!="" and self.K_end_timecode_field!=False:
                try:
                    t_tooltip_data +=    '<br><span >'+   u"Info:更新结束时间码:---->%s\n"%(t_shot_name)+ '</span>'
    
                    update_end_timecode = t_class_shot.set({self.K_end_timecode_field:t_end_timecode})
                    print u"更新结束时间码:",update_end_timecode,"t_end_timecode:",t_end_timecode
                    
                    
                    if update_end_timecode==False:
                        t_update_end_timecode_fail.append( t_shot_name+":"+t_end_timecode )
                        t_tooltip_data +=  '<br><span style="color:#FF0000;">'+  u"Error:更新结束时间码失败:---->%s\n"%(t_shot_name)+ '</span>'
                        self.t_status = False
    
                except Exception,e:
                    t_tooltip_data += '<br><span style="color:#FF0000;">'+   u"Error:更新结束时间码失败:---->%s\n"%(t_shot_name)   + '</span>'                      
                    self.t_status = False
    
            #获取第一帧缩略图
            if str( self.k_is_get_thumbnail ).lower().strip() == "y":
                t_first_pix = t_image_dict["first"]
                t_last_pix = t_image_dict["last"]
    
                t_temp_image_list = []
                if t_first_pix!="":
                    t_temp_image_list.append(t_first_pix)
                if t_last_pix!="" and t_last_pix not in t_temp_image_list:
                    t_temp_image_list.append(t_last_pix)
                try:
                    t_tooltip_data += '<br><span >'+  u"Info:更新缩略图:---->%s\n"%(t_shot_name)+ '</span>'
                    t_class_shot.set_image("shot.image",t_temp_image_list)
                except Exception,e:
                    t_update_pix_fail.append(t_shot_name)
                    t_tooltip_data += '<br><span style="color:#FF0000;">'+  u"Error:更新缩略图失败:---->%s\n"%(t_shot_name)+ '</span>'
                    self.t_status = False
    
    
            #获取最后一帧缩略图 
            if str( self.k_last_frame_thumbnail_field ).lower().strip()!="" and self.k_last_frame_thumbnail_field!=False:
                t_pix = t_image_dict["last"]
                try:
                    t_tooltip_data += '<br><span >'+  u"Info:更新最后一帧缩略图:---->%s\n"%(t_shot_name)+ '</span>'
    
                    t_class_shot.set_image(self.k_last_frame_thumbnail_field,t_pix)
                except Exception,e:
                    t_update_last_fail.append(t_shot_name)  
                    t_tooltip_data += '<br><span style="color:#FF0000;">'+ u"Info:更新最后一帧缩略图失败:---->%s\n"%(t_shot_name)+ '</span>'
                    self.t_status = False
            #复制文件
            t_is_copy_try = None 
            if str( self.k_des_file_sign ).lower().strip()!="" and self.k_des_file_sign!=False:
                t_is_copy_try = True
                try:
                    t_tooltip_data += '<br><span >'+  u"Info:拷贝文件:---->%s\n"%(t_shot_name)+ '</span>'
    
                    t_des_path = t_class_shot.get_dir( [self.k_des_file_sign] )[0][self.k_des_file_sign]
                    t_sou_path = t_path
                    t_sou = t_sou_path.replace("\\","/")
                    t_des = t_des_path.replace("\\","/") + "/" +os.path.basename(com_replace_path(t_sou))
                    if os.path.isfile(t_sou):
                        t_res = com_copy(t_sou, t_des, a_fail_str = "")
                    else:
                        t_res = com_copy(t_sou, t_des_path.replace("\\","/") , a_fail_str = "", a_is_folder_son = True)
                    if t_res!="":
                        t_tooltip_data += '<br><span style="color:#FF0000;">'+  u"Error:拷贝失败:---->%s\n"%(t_shot_name) + '</span>'
                        self.t_status = False
                        t_copy_file_fail.append(t_shot_name)
                        t_is_copy_try = False      
    
    
                except Exception,e:
                    t_tooltip_data +=  '<br><span style="color:#FF0000;">'+  u"Error:拷贝失败:---->%s\n"%(t_shot_name) + '</span>'
                    t_copy_file_fail.append(t_shot_name)
                    t_is_copy_try = False
                    self.t_status = False
    
    
    
            #--添加source字段标识
            if str( self.K_source_field ).lower().strip()!="" and self.K_source_field!=False:
                if t_is_copy_try==True:
                    try:
                        t_tooltip_data += '<br><span >'+  u"Info:更新素材字段:---->%s\n"%(t_shot_name)+ '</span>'
    
                        t_class_shot.set({self.K_source_field:t_des})
                    except Exception,e:
                        t_tooltip_data += '<br><span style="color:#FF0000;">'+  u"Info:更新素材字段失败:---->%s\n"%(t_shot_name)+ '</span>'
                        t_update_source_fail.append(t_shot_name)
                        self.t_status = False
    
    
                elif t_is_copy_try==None:
                    try:
                        t_tooltip_data += '<br><span >'+  u"Info:更新素材字段:---->%s\n"%(t_shot_name)+ '</span>'
                        t_class_shot.set({self.K_source_field:t_path.replace("\\","/")})
                    except Exception,e:
                        t_tooltip_data +='<br><span style="color:#FF0000;">'+   u"Info:更新素材字段失败:---->%s\n"%(t_shot_name)+ '</span>'
                        self.t_status = False
                        t_update_source_fail.append(t_shot_name)
    
    
            if self.t_status == True:
                self.sig_status.emit(t_row, "ok", t_tooltip_data)
                
            else:
                self.sig_status.emit(t_row, "error",t_tooltip_data)
    
        if  t_update_source_fail==[] and t_init_shot_fail == [] and t_check_shot_fail==[] and t_copy_file_fail==[] and t_create_shot_fail==[] and t_update_frame_fail==[] and t_update_pix_fail==[] and t_update_last_fail==[] and t_update_fps_fail==[] and t_update_resolution_fail==[]:
            self.sig_status.emit(0,u"完成",t_tooltip_data)      
        else:
            self.sig_status.emit(0,u"有错",t_tooltip_data)
        self.sig_thread_status.emit("finish")

    def get_image_dict(self, a_file_path_list):#取缩略图
        t_dict = {"first":"", "last":""}
        if self.k_action == "image":#表示是序列
            if len(a_file_path_list)>=1:
                t_dict["first"]=a_file_path_list[0]
                t_dict["last"]=a_file_path_list[-1]

        else:
            t_mov_path=a_file_path_list[0]
            if str( self.k_is_get_thumbnail ).lower().strip()=="y":
                t_first_pix = unicode( ct.com().get_tmp_path() ).replace("\\","/") + "/" + ct.com().uuid() +".png"
                ct.mov().get_mov_thumbnail( t_mov_path , t_first_pix )
                t_dict["first"]=t_first_pix
            if str( self.k_last_frame_thumbnail_field ).lower().strip()!="" and self.k_last_frame_thumbnail_field!=False:
                t_last_pix = unicode( ct.com().get_tmp_path() ).replace("\\","/") + "/" + ct.com().uuid() +".png"
                ct.mov().get_mov_thumbnail( t_mov_path , t_last_pix, True )
                t_dict["last"]=t_last_pix 
        return t_dict

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = create_shot_widget()
    sys.exit( app.exec_() )