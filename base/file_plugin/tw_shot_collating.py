# -*- coding: utf-8 -*-
#Author  :黄骁颖
#Time    :2018.06.19
#Describe: 改为多线程
#          New finishing
#          fps,width,height
#          shot combobox
#          cgtw_v5( 暂时的版本,后续要整改,所以暂时维持可以使用,所以没有使用通用方法 )
#          CgTeamWork V5整合

import os
import re
import sys
import time
import json
import shutil
import datetime
import functools
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
from   com_message_box   import *
from   cgtw              import *
from   com_function      import *
from   com_widget        import *
class collating_file(widget):
    COL_FILENAME = 0
    COL_SHOT     = 1
    COL_IS_RULE  = 2
    COL_SRC_PATH = 3
    COL_STATE    = 4
    
    
    ROLE_IS_SUBMI  =  32
    ROLE_IS_MOVE_OLD_TO_HISTROY = 33
    ROLE_IS_MOVE_SAME_TO_HISTROY = 34
    ROLE_IS_HISTORY_WITH_DATETIME = 35
    ROLE_IS_MOVE_TO_HISTROY_ADD_VERSION = 36
    ROLE_RULE = 37
    ROLE_PATH = 38
    ROLE_WORK_TAB_ID  =  39
    ROLE_CHECK = 42
    
    
    def __init__(self):
        super(collating_file, self).__init__()
        self.__ui__()
        self.__cgtw__()
    def __cgtw__(self):
        self.set_UI()
        try:
            self.m_tw = tw()
            self.m_database       = self.m_tw.sys().get_sys_database()
            self.class_shot       = self.m_tw.info_module(self.m_database,"shot")
            self.class_shot_work  = self.m_tw.task_module(self.m_database,"shot")
            self.class_pipeline   = self.m_tw.pipeline(self.m_database)
            self.class_eps        = self.m_tw.info_module(self.m_database,"eps")
            self.class_file       = self.m_tw.filebox(self.m_database)  
        except:
            message().error(u"连接CGteamwork失败!")
        #----pipeline
        try:
            t_pipeline_list       = self.class_pipeline.get_with_module("shot",["name","#id"])
        except:
            t_pipeline_list       = False
        if type(t_pipeline_list) != list or len(t_pipeline_list) == 0:
            message().error(u"取制作阶段列表失败, 请确认是否有配置制作阶段")
        for i in t_pipeline_list:
            self.m_pip_combo.addItem(i["name"],i["id"])
        #----eps
        try:
            self.class_eps.init_with_filter([[u"eps.eps_name","has","%"]])
            t_eps_list = self.class_eps.get(["eps.eps_name"])
        except:
            t_eps_list = False
        if  type(t_eps_list) != list or  len(t_eps_list) == 0:
            message.error(u"读取集数列表失败...")
        for eps in  sorted(t_eps_list):
            self.m_eps_combo.addItem(eps['eps.eps_name'],eps["id"])
            
        self.is_check_frame_rate  = self.m_tw.sys().get_argv_key("is_check_frame_rate")
        self.is_check_frame       = self.m_tw.sys().get_argv_key("is_check_frame")
        self.set_style()
        self.show()

    def set_UI(self):
        self.setMinimumSize(800,500)
        self.m_title_label.setText(u"复制文件")

        self.m_tablewidget = QTableWidget()
        self.m_tablewidget.setRowCount(0)
        self.m_tablewidget.setColumnCount(5)      
        self.m_tablewidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.m_tablewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.m_tablewidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.m_tablewidget.setSelectionMode(QAbstractItemView.ExtendedSelection)      
        self.m_tablewidget.verticalHeader().setVisible(False)
        self.m_tablewidget.setHorizontalHeaderLabels([u"文件名",u"镜头号",u"是否符合命名规则",u"源路径",u"状态"])  
        self.m_tablewidget.setDragEnabled(True)
        self.m_tablewidget.setDragDropMode(QAbstractItemView.DropOnly)
        self.m_tablewidget.dropEvent = self.dropEvent
        self.m_tablewidget.dragEnterEvent = self.dragEnterEvent
        self.m_tablewidget.dragMoveEvent = self.dragMoveEvent           
        self.parent_lay.addWidget(self.m_tablewidget)
        
        self.m_tablewidget.itemClicked.connect(self.slt_show_tooltip)
        

        self.m_tablewidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.m_tablewidget.customContextMenuRequested.connect(self.slt_showMenu)
        
        self.menuContext = QMenu(self)
        self.actionUpdateItem = self.menuContext.addAction(u"重新上传")
        self.actionExitItem   = self.menuContext.addAction(u"取消")

        self.actionUpdateItem.triggered.connect(self.slt_update)

        
        self.m_label_eps = QLabel()
        self.m_label_eps.setText(u"集数/场次")
        self.m_eps_combo = QComboBox()
        
        self.m_label_pip = QLabel()
        self.m_label_pip.setText(u"阶段")
        self.m_pip_combo = QComboBox()
        
        self.m_label_box = QLabel()
        self.m_label_box.setText(u"文件框")
        self.m_box_combo = QComboBox()
        
        self.m_label_pix = QLabel()
        self.m_label_pix.setText(u"缩略图")        
        self.m_check_pix = QCheckBox()
        
        
        self.m_delete_button = QPushButton()
        self.m_delete_button.setText(u"删除")
        
        self.m_ok_button     = QPushButton()
        self.m_ok_button.setText(u"确定")
        
        lay_bottom_toolbar  = QHBoxLayout()
        lay_bottom_toolbar.addWidget(self.m_label_eps)
        lay_bottom_toolbar.addWidget(self.m_eps_combo)
        lay_bottom_toolbar.addSpacing(8)
        lay_bottom_toolbar.addWidget(self.m_label_pip)
        lay_bottom_toolbar.addWidget(self.m_pip_combo)
        lay_bottom_toolbar.addSpacing(8)
        lay_bottom_toolbar.addWidget(self.m_label_box)
        lay_bottom_toolbar.addWidget(self.m_box_combo)
        lay_bottom_toolbar.addSpacing(8)
        lay_bottom_toolbar.addWidget(self.m_label_pix)
        lay_bottom_toolbar.addWidget(self.m_check_pix)
        lay_bottom_toolbar.addStretch()
        lay_bottom_toolbar.addWidget(self.m_delete_button)
        lay_bottom_toolbar.addSpacing(8)
        lay_bottom_toolbar.addWidget(self.m_ok_button)        
        lay_bottom_toolbar.setContentsMargins(0,8,0,0)
        self.parent_lay.addLayout(lay_bottom_toolbar)
        self.m_eps_combo.currentIndexChanged.connect(self.slt_eps)
        self.m_pip_combo.currentIndexChanged.connect(self.slt_pipeline)
        self.m_box_combo.currentIndexChanged.connect(self.slt_filebox)
        self.m_tablewidget.itemClicked.connect(self.slt_checked_item)
        self.m_delete_button.clicked.connect(self.slt_delete)
        self.m_ok_button.clicked.connect(self.slt_ok)
        self.m_close_button.clicked.connect(self.slt_close)
    
    def slt_showMenu(self):
        self.menuContext.exec_(QCursor.pos())

    def slt_update(self):
        row_list = []

        t_list   = self.m_tablewidget.selectedItems()
        for item in t_list:
            row = item.row()
            if self.m_tablewidget.item(row, self.COL_STATE).text() == "error":
                message().error(u"请取消选择错误行",False)
                return
            if row_list.count(row)==0:
                row_list.append(row)
        row_list.sort()
        

        if row_list == []:
            message().error(u"请选择需要重新上传的镜头",False)
            return
        t_data_list = self.get_task_data(row_list, again=True)
        try:
            self.thread_work = Thread_work(t_data_list, self.class_shot_work)
            self.thread_work.SIG_ROW_STATUS.connect(self.slt_updata_status)
            self.thread_work.SIG_ALL_STATUS.connect(self.slt_all_finish)
            self.thread_work.SIG_error.connect(self.slt_thread_message)
            self.thread_work.SIG_row_running.connect(self.slt_updata_row)
            self.thread_work.start()                      
        except Exception,e:
            print "error:slt_updata"
            pass
        

        
    def slt_show_tooltip(self, a_item):
        t_row = self.m_tablewidget.row(a_item)
        if t_row >= 0:
            t_tooltip_str = self.m_tablewidget.item(t_row, self.COL_STATE).toolTip()
            if t_tooltip_str.strip() != "":
                QToolTip.showText(QCursor.pos(), t_tooltip_str)

    def get_data_from_base_name(self, rule_list, base_name):
        t_new_list = []
        for i in rule_list:
            #判断是否是纯数字的规则。。为了判断集数和镜头都是数字的。比如002_01(002为集数， 01为镜头号)
            if re.search(r'[^#^|^?^*]', i):
                #有带字母和数字
                t_res=re.search(self.change_to_regex(i), base_name)
                if t_res:
                    t_new_list.append( t_res.group(0) )                
        
            else:
                #纯数字
                for m in re.finditer(r'[0-9]+',base_name):
                    if len(m.group())==len(i):
                        t_new_list.append( m.group() )  
            
        if t_new_list == []:
            return [""]
        else:
            return t_new_list
    def change_to_regex(self, string_rule):
        return unicode(string_rule).replace("#", "[0-9]").replace("?","[a-zA-Z]").replace("*","[\s\S]*")#替换为正则表达式
    
    def get_file_rule_to_string(self, rule_list):
        t_total=""
        for i in rule_list:
            if t_total=="":
                t_total=i
            else:
                t_total=t_total+"\n"+i
        return t_total 
    def is_match_file_rule(self,a_filename,a_file_rule_list): 
        if isinstance(a_filename,(str,unicode))==False or isinstance(a_file_rule_list,list)==False:
            return False
        for rule in a_file_rule_list:
            if re.match(rule.strip().replace("#", "[0-9]").replace("?","[a-zA-Z]").replace("*","[\s\S]*"), a_filename):
                return True
        return False
    def is_error(self):
        t_error_shot=""
        t_error_rule=""
        t_error_check =''
        t_total=""
        for i in range(self.m_tablewidget.rowCount()):
            try:
                t_shot          = unicode(self.m_tablewidget.item(i, self.COL_FILENAME).data(self.ROLE_PATH).currentText())
            except:
                t_shot          = ''
            try:
                t_filename      = unicode(self.m_tablewidget.item(i, self.COL_FILENAME).text())
            except:
                t_filename      = ''
            try:
                t_is_error_rule = unicode(self.m_tablewidget.item(i, self.COL_IS_RULE).text())
            except:
                t_is_error_rule = "N"
            try:
                t_check         = unicode(self.m_tablewidget.item(i, self.COL_FILENAME).data(self.ROLE_CHECK))
            except:
                t_check         = ''
                    
            if t_shot=="":
                
                t_error_shot=t_error_shot+t_filename+"\n"
                continue
            else:
                if t_is_error_rule=="N":
                    t_error_rule=t_error_rule+t_filename+"\n"
            if t_check!='':
                t_error_check = t_error_check + t_filename +"\n"
        if t_error_rule!="" or t_error_shot!="" or t_error_check!='':
            if t_error_shot!="":
                t_total=u"没有找对应的镜头信息如下:\n"+t_error_shot+"\n"
            if t_error_rule!="":
                t_total=t_total+u"命名规则错误如下:\n"+t_error_rule
            if t_error_check!='':
                t_total=t_total+u"帧数/帧率检查错误如下:\n"+t_error_check
            message().error(t_total,False)
            return False
        return True    
    def refresh_UI(self, a_shot, base_name ,row, t_shot_list, t_filebox_id, t_combobox , t_path):
        t_shot        = a_shot
        self.class_shot_work.init_with_filter([ ["shot.shot", "=",t_shot ],"and",["eps.eps_name","=",self.m_eps_combo.currentText()],"and",["task.pipeline","=",self.m_pip_combo.currentText()]])
        id_list=self.class_shot_work.get_id_list()
        #-----------------------------
        is_fail = False
        t_tooltip_str = ""
        if id_list!=False and len(id_list)>=1:
            if os.path.isfile(t_path) and os.path.splitext(base_name)[1] in [".mov",".avi",".mp4",".rmvb"]:
                avi_info = False
                if str(self.is_check_frame).lower() == 'y':
                    try:
                        avi_info = ct.mov().get_avi_info( t_path )
                        t_frame  = self.class_shot_work.get(["shot.frame"])[0]["shot.frame"]
                        if int(float(t_frame)) != int(float(avi_info["FrameCount"])) :
                            t_tooltip_str += u"Error:帧数检查错误\n"
                            is_fail = True
                    except:
                        t_tooltip_str += u"Error:帧数检查错误\n"
                        is_fail = True
                if str(self.is_check_frame_rate).lower() == 'y':
                    try:
                        if avi_info == False:
                            avi_info = ct.mov().get_avi_info( t_path )
                        t_prj = self.m_tw.info_module("public","project")
                        t_prj.init_with_filter([["project.database",'=',self.m_database]])
                        t_rate  = t_prj.get(["project.frame_rate"])[0]["project.frame_rate"]
                        if int(float(t_rate)) != int(float(avi_info["FrameRate"])) :
                            t_tooltip_str += u"Error:帧率检查错误\n "
                    except Exception,e:
                        t_tooltip_str += u"Error:帧率检查错误\n "
                        is_fail = True
        if is_fail:
            self.m_tablewidget.item(row,self.COL_STATE).setBackground(Qt.red)
            self.m_tablewidget.item(row,self.COL_FILENAME).setData(self.ROLE_CHECK,"Y")
            self.m_tablewidget.item(row,self.COL_STATE).setText("error")
            #t_tooltip_str = self.m_tablewidget.item(row,self.COL_STATE).toolTip() + t_tooltip_str
            self.m_tablewidget.item(row,self.COL_STATE).setToolTip(t_tooltip_str)
        else:
            self.m_tablewidget.item(row,self.COL_STATE).setBackground(Qt.white)
            self.m_tablewidget.item(row,self.COL_FILENAME).setData(self.ROLE_CHECK,"")
            self.m_tablewidget.item(row,self.COL_STATE).setBackground(Qt.white)
            self.m_tablewidget.item(row,self.COL_STATE).setToolTip("")
            self.m_tablewidget.item(row,self.COL_STATE).setText("wait")
        #------------------------------------
        rule_item=QTableWidgetItem()
        temp_rule_data="N"
        #----------------------------------
        shot_name_combobox = t_combobox
        #----------------------------------                  
        if id_list==False or len(id_list)<1:
            temp_rule_data="N"
            self.m_tablewidget.item(row, self.COL_STATE).setText("error")
            t_tooltip_str = t_tooltip_str + u"没有找到对应的镜头#1\n"
            self.m_tablewidget.item(row, self.COL_STATE).setToolTip(t_tooltip_str)
            self.m_tablewidget.item(row, self.COL_STATE).setBackground(Qt.red)
            shot_name_combobox.setStyleSheet("QComboBox{border:1px solid #E5E6E7; border-radius:4px;font-size:12px;color:#666666;}"
                                             "QListView{background-color: #FFFFFF;height:50px;outline:none;}"
                                             "QListView::Item{height:24px;font-size:12px;color:#666666;outline:none;}"
                                             "QListView::Item:hover{background-color:#E9E9E9;outline:none;}"
                                             "QListView::Item:selected{background-color:#E9E9E9;outline:none;}"
                                             "QComboBox::down-arrow {image: url(" + self.m_icon_path + "/com_icon/down-arrow.png);}"
                                             "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width:24px;border:none;}"
                                             )  
            self.m_tablewidget.item(row,0).setData(self.ROLE_WORK_TAB_ID,'')

        else:
            shot_name_combobox.setStyleSheet("QComboBox{background-color:#FFFFFF;border:1px solid #E5E6E7; border-radius:4px;font-size:12px;color:#666666;}"
                                             "QListView{background-color: #FFFFFF;height:50px;outline:none;}"
                                             "QListView::Item{height:24px;font-size:12px;color:#666666;outline:none;}"
                                             "QListView::Item:hover{background-color:#E9E9E9;outline:none;}"
                                             "QListView::Item:selected{background-color:#E9E9E9;outline:none;}"
                                             "QComboBox::down-arrow {image: url(" + self.m_icon_path + "/com_icon/down-arrow.png);}"
                                             "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width:24px;border:none;}"
                                             )  
            self.m_tablewidget.item(row,self.COL_FILENAME).setData(self.ROLE_WORK_TAB_ID,id_list[0])
            filebox_data=self.class_shot_work.get_filebox_with_filebox_id(t_filebox_id)
            if type(filebox_data)!=dict:
                temp_rule_data="N"
            else:
                t_rule_string=self.get_file_rule_to_string(filebox_data["rule"])
                rule_item.setToolTip(t_rule_string)
                if self.is_match_file_rule(base_name,unicode(t_rule_string).split("\n")):
                    temp_rule_data="Y"  
                rule_item.setData(self.ROLE_IS_SUBMI, filebox_data["is_submit"])
                rule_item.setData(self.ROLE_IS_MOVE_OLD_TO_HISTROY, filebox_data["is_move_old_to_history"])
                rule_item.setData(self.ROLE_IS_MOVE_SAME_TO_HISTROY, filebox_data["is_move_same_to_history"])
                rule_item.setData(self.ROLE_IS_HISTORY_WITH_DATETIME, filebox_data["is_in_history_add_datetime"])
                rule_item.setData(self.ROLE_IS_MOVE_TO_HISTROY_ADD_VERSION, filebox_data["is_in_history_add_version"])
                rule_item.setData(self.ROLE_RULE, filebox_data["rule"])
                rule_item.setData(self.ROLE_PATH, filebox_data["path"])
        rule_item.setText(temp_rule_data)
        if temp_rule_data=="N":
            self.m_tablewidget.item(row, self.COL_STATE).setText("error")
            t_tooltip_str = t_tooltip_str + u"镜头号规则不符#1\n"
            self.m_tablewidget.item(row, self.COL_STATE).setToolTip(t_tooltip_str)
            self.m_tablewidget.item(row, self.COL_STATE).setBackground(Qt.red)
            
        self.m_tablewidget.setItem(row, self.COL_IS_RULE,rule_item)
    #----------------------------------------slot-------------------------------------
    def slt_eps(self):
        self.m_tablewidget.setRowCount(0)
        self.m_shot_rule_list=[]
        try:
            self.class_shot.init_with_filter([[u"eps.eps_name","=",self.m_eps_combo.currentText() ]])
            data_list=self.class_shot.get(["shot.shot"])
        except:
            data_list = False
        if type(data_list)!=list:
            return
        for data in data_list:
            shot    = data["shot.shot"]
            output  = re.sub('[0-9]', '#', shot)
            if self.m_shot_rule_list.count(output)==0:
                self.m_shot_rule_list.append(output)
        self.m_shot_rule_list.sort()
        self.m_shot_rule_list.reverse()
    def slt_pipeline(self, pipeline_int):
        self.m_tablewidget.setRowCount(0)
        self.m_box_combo.clear()
        try:
            pipeline_int_id = self.m_pip_combo.itemData( pipeline_int )
            data_list       = self.class_file.get_with_pipeline_id(pipeline_int_id,"shot")
        except:
            data_list       = False
        if  type(data_list) != list or  len(data_list) == 0:
            message().error(u"读取文件框名失败...",False)
            return
        for data in data_list:
            self.m_box_combo.addItem(data['title'], data['id'])   
    def slt_filebox(self):
        self.m_tablewidget.setRowCount(0)
    def slt_checked_item(self):
        pass
    def slt_close(self):
        sys.exit()
    def slt_delete(self):
        t_list=self.m_tablewidget.selectedItems()
        row_list=[]
        for item in t_list:
            row=item.row()
            if row_list.count(row)==0:
                row_list.append(row)
        row_list.sort()
        t_count=len(row_list)
        for i in range(t_count):
            self.m_tablewidget.removeRow(row_list[t_count-i-1])
    
    #获取所有任务信息 返回列表
    def get_task_data(self, row_list, again = False ):
        if again == True: #如果是右键选中重新上传
            t_count = len(row_list)
        else:
            t_count = row_list

        is_get_thumbnail   = False
        t_tooltip_str        = ""
        if self.m_check_pix.isChecked():
            is_get_thumbnail = True
            
        t_data_list  = []
        for i in range(t_count):
            if again == True:  #如果是右键选中重新上传
                i = row_list[t_count-i-1]
            work_tab_id     = self.m_tablewidget.item(i, self.COL_FILENAME).data(self.ROLE_WORK_TAB_ID)
            t_sou           = unicode(self.m_tablewidget.item(i, self.COL_SRC_PATH).text())
            
            is_submit       = False
            if unicode(self.m_tablewidget.item(i, self.COL_IS_RULE).data(self.ROLE_IS_SUBMI))=="Y":
                is_submit   = True
                
            is_move_old_to_history     = False
            if unicode(self.m_tablewidget.item(i, self.COL_IS_RULE).data(self.ROLE_IS_MOVE_OLD_TO_HISTROY))=="Y":
                is_move_old_to_history = True
                
            is_move_same_to_history     = False
            if unicode(self.m_tablewidget.item(i, self.COL_IS_RULE).data(self.ROLE_IS_MOVE_SAME_TO_HISTROY))=="Y":
                is_move_same_to_history = True
            
            is_history_with_datetime     = False
            if unicode(self.m_tablewidget.item(i, self.COL_IS_RULE).data(self.ROLE_IS_HISTORY_WITH_DATETIME))=="Y":
                is_history_with_datetime = True
            
            is_move_to_history_add_version     = False
            if unicode(self.m_tablewidget.item(i, self.COL_IS_RULE).data(self.ROLE_IS_MOVE_TO_HISTROY_ADD_VERSION))=="Y":
                is_move_to_history_add_version = True
    
            des_dir        = unicode(self.m_tablewidget.item(i, self.COL_IS_RULE).data(self.ROLE_PATH))           
            temp_rule_list = list(self.m_tablewidget.item(i, self.COL_IS_RULE).data(self.ROLE_RULE))
            
            t_data_list.append({"row":i,"work_tab_id":work_tab_id,"sou_path":t_sou,"is_submit":is_submit,
                                "is_move_old_to_history":is_move_old_to_history,"is_move_same_to_history":is_move_same_to_history,
                                "is_history_with_datetime":is_history_with_datetime,"is_move_to_history_add_version":is_move_to_history_add_version,
                                "des_dir":des_dir,"temp_rule_list":temp_rule_list,"is_get_thumbnail":is_get_thumbnail
                                })
        return t_data_list
    
    def slt_ok(self):
        if self.m_tablewidget.rowCount()==0:
            message().error(u"请拖入文件",False)
            return
        if self.is_error()==False:
            return
        
        t_data_list = self.get_task_data(self.m_tablewidget.rowCount())
        try:
            self.thread_work = Thread_work(t_data_list, self.class_shot_work)
            self.thread_work.SIG_ROW_STATUS.connect(self.slt_updata_status)
            self.thread_work.SIG_ALL_STATUS.connect(self.slt_all_finish)
            self.thread_work.SIG_error.connect(self.slt_thread_message)
            self.thread_work.SIG_row_running.connect(self.slt_updata_row)
            self.thread_work.start()   
            self.m_ok_button.setEnabled(False)
        except Exception,e:
            pass     
        
    #任务进行时 行选中
    def slt_updata_row(self,a_row):
        self.m_tablewidget.setCurrentItem(self.m_tablewidget.item(a_row, 0))
    #弹错误消息框
    def slt_thread_message(self,a_message):
        message().error(a_message,False)
        
    #更改状态栏
    def slt_updata_status(self, a_row, a_status, a_tooltip_str):
        
        if a_status == u"错误" :
            self.m_tablewidget.item(a_row, self.COL_STATE).setText("错误")
            self.m_tablewidget.item(a_row, self.COL_STATE).setBackground(Qt.red)
            
            t_tooltip_str = self.m_tablewidget.item(a_row, self.COL_STATE).toolTip() + a_tooltip_str
            self.m_tablewidget.item(a_row, self.COL_STATE).setToolTip(t_tooltip_str)

        else:
            self.m_tablewidget.item(a_row, self.COL_STATE).setText("完成")
            self.m_tablewidget.item(a_row, self.COL_STATE).setBackground(Qt.white)  
        
    #所有任务完成提示
    def slt_all_finish(self,a_is_ok) :
        if not a_is_ok:
            message().error(u"存在错误,请查看状态列", False)
        else:
            message().info(u"完成")            
        self.m_ok_button.setEnabled(True)
            
    def slt_change_combobox(self, a_combobox, a_base_name, t_shot_list, t_filebox_id, t_path, a_index):
        for i in range(self.m_tablewidget.rowCount()):
            if self.m_tablewidget.item(i, self.COL_FILENAME).data(self.ROLE_PATH) == a_combobox:
                self.refresh_UI(a_combobox.currentText(), a_base_name, i, t_shot_list, t_filebox_id, a_combobox, t_path)
    #----------------------------------------style------------------------------------
    def set_style(self):
        self.m_ok_button.setFixedSize(60,28)
        self.m_ok_button.setStyleSheet("QPushButton{background-color:#108ee9;color:#FFFFFF;font-size:12px;border-radius:4px;}"
                                         "QPushButton:hover{background-color:#1083E0; border-radius:4px; font-size:12px; color:#FFFFFF;}"
                                         )   
        self.m_label_eps.setStyleSheet("QLabel{color:#666666;font-size:12px;}")
        self.m_label_pip.setStyleSheet("QLabel{color:#666666;font-size:12px;}")
        self.m_label_box.setStyleSheet("QLabel{color:#666666;font-size:12px;}")
        self.m_label_pix.setStyleSheet("QLabel{color:#666666;font-size:12px;}")
        self.m_eps_combo.setView(QListView())
        self.m_eps_combo.setFixedSize(130,24)
        self.m_eps_combo.setStyleSheet("QComboBox{background-color:#FFFFFF;border:1px solid #E5E6E7; border-radius:4px;font-size:12px;color:#666666;}"
                                       "QListView{background-color: #FFFFFF;height:50px;outline:none;}"
                                       "QListView::Item{height:24px;font-size:12px;color:#666666;outline:none;}"
                                       "QListView::Item:hover{background-color:#E9E9E9;outline:none;}"
                                       "QListView::Item:selected{background-color:#E9E9E9;outline:none;}"
                                       "QComboBox::down-arrow {image: url(" + self.m_icon_path + "/com_icon/down-arrow.png);}"
                                       "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width:24px;border:none;}"
                                       )     
        self.m_pip_combo.setView(QListView())
        self.m_pip_combo.setFixedSize(130,24)
        self.m_pip_combo.setStyleSheet("QComboBox{background-color:#FFFFFF;border:1px solid #E5E6E7; border-radius:4px;font-size:12px;color:#666666;}"
                                       "QListView{background-color: #FFFFFF;height:50px;outline:none;}"
                                       "QListView::Item{height:24px;font-size:12px;color:#666666;outline:none;}"
                                       "QListView::Item:hover{background-color:#E9E9E9;outline:none;}"
                                       "QListView::Item:selected{background-color:#E9E9E9;outline:none;}"
                                       "QComboBox::down-arrow {image: url(" + self.m_icon_path + "/com_icon/down-arrow.png);}"
                                       "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width:24px;border:none;}"
                                       )       
        self.m_box_combo.setView(QListView())
        self.m_box_combo.setFixedSize(130,24)
        self.m_box_combo.setStyleSheet("QComboBox{background-color:#FFFFFF;border:1px solid #E5E6E7; border-radius:4px;font-size:12px;color:#666666;}"
                                       "QListView{background-color: #FFFFFF;height:50px;outline:none;}"
                                       "QListView::Item{height:24px;font-size:12px;color:#666666;outline:none;}"
                                       "QListView::Item:hover{background-color:#E9E9E9;outline:none;}"
                                       "QListView::Item:selected{background-color:#E9E9E9;outline:none;}"
                                       "QComboBox::down-arrow {image: url(" + self.m_icon_path + "/com_icon/down-arrow.png);}"
                                       "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width:24px;border:none;}"
                                       )
        self.m_delete_button.setFixedSize(60,28)
        self.m_delete_button.setStyleSheet("QPushButton{background-color:#FFFFFF;color:#666666;font-size:12px;border-radius:4px;border:1px solid #999999;}"
                                           "QPushButton:hover{background-color:#FFFFFF; border-radius:4px; font-size:12px; color:#0F87DE;border:1px solid #0F87DE}"
                                           ) 
        self.m_tablewidget.setStyleSheet("QTableWidget{font-size:12px;color:#666666;border:1px solid #E5E6E7;border-radius:4px;outline:none;}"
                                         "QHeaderView::section{background:red;color:#666666;outline:none;}"
                                         "QHeaderView{min-height:32px;outline:none;}"
                                         )  
        self.m_check_pix.setStyleSheet("QCheckBox::indicator:checked{width:16px;height:16px;border:1px solid #108ee9;border-radius:4px; image: url("+ self.m_icon_path +"/com_icon/is_checked.png);background-color:#108ee9;}"
                                       "QCheckBox::indicator {width:18px;height:18px;}"
                                       "QCheckBox::indicator:unchecked{width:16px;height:16px;border:1px solid #999999;border-radius:4px;}"
                                       )
    #----------------------------------------event------------------------------------
    def dropEvent(self,e):
        t_eps        = unicode( self.m_eps_combo.currentText() )
        t_pipeline   = unicode( self.m_pip_combo.currentText() )
        
        
        t_filebox_id = self.m_box_combo.itemData(self.m_box_combo.currentIndex())
        if t_eps == '' :
            message().error(u"集数/场次不能为空,请先选择", False)
            return
        if t_pipeline == '':
            message().error(u"阶段不能为空,请先选择",False)
            return
        if t_filebox_id == '':
            message().error(u"文件框名不能为空,请先选择",False)
            return
        mime = e.mimeData()
        if mime.hasUrls():
            self.m_tablewidget.setRowCount(0)
            for url in mime.urls():
                t_path        = unicode(url.toLocalFile())
                t_path        = com_replace_path( t_path )
                row           = self.m_tablewidget.rowCount()
                base_name     = os.path.basename(com_replace_path(t_path))
                t_tooltip_str = ""
                self.m_tablewidget.insertRow(row)
                t_shot_list   = self.get_data_from_base_name(self.m_shot_rule_list, os.path.splitext(base_name)[0])
                t_shot        = t_shot_list[0]
                self.m_tablewidget.setItem(row, self.COL_FILENAME, QTableWidgetItem(base_name))
                self.m_tablewidget.setItem(row, self.COL_SRC_PATH, QTableWidgetItem(t_path))
                self.m_tablewidget.setItem(row, self.COL_STATE, QTableWidgetItem(""))
                self.class_shot_work.init_with_filter([ ["shot.shot", "=",t_shot ],"and",["eps.eps_name","=",self.m_eps_combo.currentText()],"and",["task.pipeline","=",self.m_pip_combo.currentText()]])
                id_list=self.class_shot_work.get_id_list()
                #-----------------------------
                is_fail = False
                if id_list!=False and len(id_list)>=1:
                    if os.path.isfile(t_path) and os.path.splitext(base_name)[1] in [".mov",".avi",".mp4",".rmvb"]:
                        avi_info = False
                        if str(self.is_check_frame).lower() == 'y':
                            try:
                                avi_info = ct.mov().get_avi_info( t_path )
                                t_frame  = self.class_shot_work.get(["shot.frame"])[0]["shot.frame"]
                                if int(float(t_frame)) != int(float(avi_info["FrameCount"])) :
                                    t_tooltip_str += u"Error:帧数检查错误\n"
                                    is_fail = True
                                    
                            except:
                                t_tooltip_str += u"Error:帧数检查错误\n"
                                is_fail = True
                        if str(self.is_check_frame_rate).lower() == 'y':
                            try:
                                if avi_info == False:
                                    avi_info = ct.mov().get_avi_info( t_path )
                                t_prj = self.m_tw.info_module("public","project")
                                t_prj.init_with_filter([["project.database",'=',self.m_database]])
                                t_rate  = t_prj.get(["project.frame_rate"])[0]["project.frame_rate"]
                                if int(float(t_rate)) != int(float(avi_info["FrameRate"])) :
                                    t_tooltip_str += u"Error:帧率检查错误\n"
                                    is_fail = True
                            except:
                                t_tooltip_str += u"Error:帧率检查错误\n"
                                is_fail = True
                if is_fail:
                    self.m_tablewidget.setItem(row, self.COL_STATE, QTableWidgetItem("error"))
                    self.m_tablewidget.item(row,self.COL_STATE).setBackground(Qt.red)
                    self.m_tablewidget.item(row,self.COL_FILENAME).setData(self.ROLE_CHECK,"Y")
                    t_tooltip_str = self.m_tablewidget.item(row,self.COL_STATE).toolTip() + t_tooltip_str
                    self.m_tablewidget.item(row,self.COL_STATE).setToolTip(t_tooltip_str)
                else:
                    self.m_tablewidget.item(row,self.COL_STATE).setBackground(Qt.white)
                    self.m_tablewidget.item(row,self.COL_FILENAME).setData(self.ROLE_CHECK,"")
                    self.m_tablewidget.setItem(row, self.COL_STATE, QTableWidgetItem("wait"))
                #------------------------------------
                rule_item=QTableWidgetItem()
                temp_rule_data="N"
                #----------------------------------
                shot_name_widget   = QWidget()
                shot_name_lay      = QVBoxLayout()
                shot_name_combobox = QComboBox()
                shot_name_combobox.setView(QListView())
                shot_name_combobox.setFixedHeight(28)
                for t_shot_name in t_shot_list:
                    shot_name_combobox.addItem(t_shot_name)                    
                shot_name_lay.addWidget(shot_name_combobox)   
                shot_name_lay.setContentsMargins(0,0,0,0)
                shot_name_widget.setLayout(shot_name_lay)
                self.m_tablewidget.setCellWidget(row, self.COL_SHOT, shot_name_widget)
                self.m_tablewidget.item(row,self.COL_FILENAME).setData(self.ROLE_PATH,shot_name_combobox)     
                shot_name_combobox.currentIndexChanged.connect( functools.partial(self.slt_change_combobox, shot_name_combobox, base_name, t_shot_list, t_filebox_id, t_path))
                #----------------------------------                  
                
                if id_list==False or len(id_list)<1:
                    temp_rule_data="N"
                    self.m_tablewidget.item(row, self.COL_STATE).setText("error")
                    t_tooltip_str = self.m_tablewidget.item(row, self.COL_STATE).toolTip() + u"没有找到对应的镜头\n"
                    self.m_tablewidget.item(row, self.COL_STATE).setToolTip(t_tooltip_str)
                    self.m_tablewidget.item(row, self.COL_STATE).setBackground(Qt.red)
                    shot_name_combobox.setStyleSheet("QComboBox{border:1px solid #E5E6E7; border-radius:4px;font-size:12px;color:#666666;}"
                                                     "QListView{background-color: #FFFFFF;height:50px;outline:none;}"
                                                     "QListView::Item{height:24px;font-size:12px;color:#666666;outline:none;}"
                                                     "QListView::Item:hover{background-color:#E9E9E9;outline:none;}"
                                                     "QListView::Item:selected{background-color:#E9E9E9;outline:none;}"
                                                     "QComboBox::down-arrow {image: url(" + self.m_icon_path + "/com_icon/down-arrow.png);}"
                                                     "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width:24px;border:none;}"
                                                     )  
                    self.m_tablewidget.item(row,self.COL_FILENAME).setData(self.ROLE_WORK_TAB_ID,'')

                else:
                    shot_name_combobox.setStyleSheet("QComboBox{background-color:#FFFFFF;border:1px solid #E5E6E7; border-radius:4px;font-size:12px;color:#666666;}"
                                                     "QListView{background-color: #FFFFFF;height:50px;outline:none;}"
                                                     "QListView::Item{height:24px;font-size:12px;color:#666666;outline:none;}"
                                                     "QListView::Item:hover{background-color:#E9E9E9;outline:none;}"
                                                     "QListView::Item:selected{background-color:#E9E9E9;outline:none;}"
                                                     "QComboBox::down-arrow {image: url(" + self.m_icon_path + "/com_icon/down-arrow.png);}"
                                                     "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width:24px;border:none;}"
                                                     )  
                    self.m_tablewidget.item(row,self.COL_FILENAME).setData(self.ROLE_WORK_TAB_ID,id_list[0])
                    filebox_data=self.class_shot_work.get_filebox_with_filebox_id(t_filebox_id)
                    if type(filebox_data)!=dict:
                        temp_rule_data="N"
                    else:
                        t_rule_string=self.get_file_rule_to_string(filebox_data["rule"])
                        rule_item.setToolTip(t_rule_string)
                        if self.is_match_file_rule(base_name,unicode(t_rule_string).split("\n")):
                            temp_rule_data="Y"  
                        rule_item.setData(self.ROLE_IS_SUBMI, filebox_data["is_submit"])
                        rule_item.setData(self.ROLE_IS_MOVE_OLD_TO_HISTROY, filebox_data["is_move_old_to_history"])
                        rule_item.setData(self.ROLE_IS_MOVE_SAME_TO_HISTROY, filebox_data["is_move_same_to_history"])
                        rule_item.setData(self.ROLE_IS_HISTORY_WITH_DATETIME, filebox_data["is_in_history_add_datetime"])
                        rule_item.setData(self.ROLE_IS_MOVE_TO_HISTROY_ADD_VERSION, filebox_data["is_in_history_add_version"])
                        rule_item.setData(self.ROLE_RULE, filebox_data["rule"])
                        rule_item.setData(self.ROLE_PATH, filebox_data["path"])
                rule_item.setText(temp_rule_data)
                if temp_rule_data=="N":
                    self.m_tablewidget.item(row, self.COL_STATE).setText("error")
                    t_tooltip_str = self.m_tablewidget.item(row, self.COL_STATE).toolTip() + u"镜头号规则不符\n"
                    self.m_tablewidget.item(row, self.COL_STATE).setToolTip(t_tooltip_str)
                    self.m_tablewidget.item(row, self.COL_STATE).setBackground(Qt.red)
                self.m_tablewidget.setItem(row, self.COL_IS_RULE,rule_item)
    def dragMoveEvent(self,e):
        e.acceptProposedAction()

    def dragEnterEvent(self,e):
        e.accept()  
        
class Thread_work(QThread):
    SIG_ALL_STATUS            = Signal(bool)
    SIG_ROW_STATUS            = Signal(int,str,str)
    SIG_error                 = Signal(str)
    SIG_row_running           = Signal(int)
    def __init__(self,a_data_list, a_class_work):
        super(Thread_work,self).__init__()    
        self.m_data_list       = a_data_list
        self.class_shot_work   = a_class_work
        self.m_all_status      = True
    def run(self):
        #try:
        self.do()
        #except :
            #self.SIG_error.emit(u"上传错误")
        
    def do(self):
        for data in self.m_data_list:
            t_time        = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(time.time()))
            t_row         = data['row']
            t_work_tab_id = data['work_tab_id']
            t_sou         = data['sou_path']
            t_is_submit   = data['is_submit']
            t_is_move_old_to_history         = data['is_move_old_to_history']
            t_is_move_same_to_history        = data['is_move_same_to_history']
            t_is_history_with_datetime       = data['is_history_with_datetime']
            t_is_move_to_history_add_version = data['is_move_to_history_add_version']
            t_des_dir          = data['des_dir']
            t_temp_rule_list   = data['temp_rule_list']
            t_is_get_thumbnail = data['is_get_thumbnail']
            self.SIG_row_running.emit(t_row)
            t_tooltip_str =  ""
            rule_list     = []
            for n in t_temp_rule_list:
                rule_list.append(unicode(n))
            is_file=False
            if os.path.isfile(unicode(t_sou)):
                is_file=True
                

            #t_is_move_same_to_history = False
            #t_is_submit  = True
            #t_is_move_old_to_history = True

            if t_is_submit:
                if t_is_move_old_to_history:
                    try:
                        t_data = self.move_check_file_list(t_des_dir, t_time, t_is_history_with_datetime, t_is_move_to_history_add_version, t_work_tab_id)
                    except:
                        t_tooltip_str += u'move_check_file_list is fail \n'
                        
                    if t_data != "":
                        t_tooltip_str += t_data
                
                if t_is_move_same_to_history:
                    try:
                        self.move_same_file_list(t_sou, t_des_dir, is_file, t_time, t_is_history_with_datetime, t_is_move_to_history_add_version)
                    except:
                        t_tooltip_str += u'move_same_file_list is fail \n'
            else:
                if t_is_move_old_to_history:
                    try:
                        self.move_all_rule_file_list(t_des_dir, rule_list, t_time, t_is_history_with_datetime, t_is_move_to_history_add_version) 
                    except :
                        t_tooltip_str += u'move_old_to_history is fail \n'    
                        
                if t_is_move_same_to_history:
                    try:
                        self.move_same_file_list(t_sou, t_des_dir, is_file, t_time, t_is_history_with_datetime, t_is_move_to_history_add_version)
                    except :
                        t_tooltip_str += u'move_same_file_list is fail \n'
        
            t_name   = os.path.basename(com_replace_path(t_sou))
            if os.path.exists(t_des_dir)==False:
                os.makedirs(t_des_dir) 
            if is_file:
                des_file_path = t_des_dir + "/" + t_name

                ct.file().copy_file(t_sou, des_file_path)

                if os.path.exists(des_file_path) !=True:
                    t_tooltip_str += u"复制失败\n"
                else:
                    if t_is_submit:
                        if self.submit(t_name, [des_file_path], t_work_tab_id)==False:
                            submit_fail=submit_fail+"\n"+t_name
                    if t_is_get_thumbnail:
                        if self.file_get_thumbnail(t_sou, t_work_tab_id)==False:
                            t_tooltip_str += u"生成缩略图失败\n"             
            else:
                try:
                    self.copy_tree(t_sou, t_des_dir+"/"+t_name)
                except:
                    t_tooltip_str += u"复制失败\n"
                if os.path.exists(t_des_dir) !=True:
                    t_tooltip_str += u"复制失败\n"
                else:
                    if t_is_submit:
                        t_des_file_list=self.get_folder_des_list(t_sou, t_des_dir+"/"+t_name)
                        if self.submit(t_name, t_des_file_list, t_work_tab_id)==False:
                            submit_fail=submit_fail+"\n"+t_name
                    if t_is_get_thumbnail:
                        if self.folder_get_thumbnail(t_sou, t_work_tab_id)==False:
                            t_tooltip_str += u"生成缩略图失败\n"
        
            if t_tooltip_str != "":
                self.SIG_ROW_STATUS.emit(t_row,u"错误",t_tooltip_str)
                self.m_all_status =False
            else:
                self.SIG_ROW_STATUS.emit(t_row,u"完成",t_tooltip_str)
            
        if self.m_all_status == False:
            self.SIG_ALL_STATUS.emit(False)
        else:
            self.SIG_ALL_STATUS.emit(True)
            
    def move_check_file_list(self, des_dir, t_time, is_history_with_datetime, is_move_to_history_add_version, work_tab_id):
        #取的是提交的文件列表
        t_list=[]
        self.class_shot_work.init_with_id([work_tab_id])

        t_data_list = self.class_shot_work.get(["task.submit_file_path"])
        if t_data_list ==False or len(t_data_list)==0:
            return u"读取数据库失败"
        else: 
            temp=t_data_list[0]["task.submit_file_path"]
            if temp is not None and len(temp)>4:
                file_json=json.loads(temp)
                file_path_list=file_json['file_path']
                if isinstance(file_path_list,list):
                    for sou_file in file_path_list:
                        if os.path.exists(sou_file):  
                            t_list.append(sou_file)
                            
        if len(t_list)>0:
            if unicode(des_dir).lower()==unicode(os.path.dirname(unicode(t_list[0]).lower())):#是文件

                self.move_to_history(t_list, t_time, is_history_with_datetime, is_move_to_history_add_version, des_dir, True)
            else:
                t_name=""
                temp_path=t_list[0].replace("\\","/")
                temp_list=unicode(temp_path).split("/")


                for i in temp_list:
                    if unicode("/"+des_dir+"/").find(unicode("/"+i+"/"))==-1:
                        t_name=i
                        break
                t_name = os.path.basename(os.path.dirname(temp_path))
                self.move_to_history(t_list, t_time, is_history_with_datetime, is_move_to_history_add_version, des_dir, False, t_name)
        return ""
    def folder_get_thumbnail(self, sou_dir, work_tab_id):
        
        sou_image_list=ct.file().get_file_with_walk_folder(sou_dir, ["*.*"])
        if len(sou_image_list)>0:
            try:
                self.class_shot_work.init_with_id([work_tab_id])
                t_res=self.class_shot_work.set_image("task.image", sou_image_list[0])
                return  t_res
            except:
                return False
        return True 
    def submit(self, name, t_des_file_list, work_tab_id):
        try:
            self.class_shot_work.init_with_id([work_tab_id])
            return self.class_shot_work.submit(t_des_file_list, "")
        except:
            return False
    def get_version_file(self, des_path):
        base_name=os.path.basename(unicode(com_replace_path(des_path)))
        t_path = os.path.dirname(des_path)
        t_filename = os.path.splitext(base_name)[0]
        t_ext=os.path.splitext(base_name)[1]
        temp=""
        for i in range(1000):
            if i>0:
                if i<10:
                    temp="_v0"+str(i)
                else:
                    temp="_v"+str(i)
                t_max_path=t_path+"/" + t_filename+temp+t_ext
                if not os.path.exists(t_max_path):
                    return t_max_path   
    def get_version_folder(self, file_list, t_dir, des_dir, t_name):

        t_list=[]
        t_ver=""
        temp=""

        for i in range(1000):
            if i>0:
                if i<10:
                    temp="_v0"+str(i)
                else:
                    temp="_v"+str(i)

                temp_path=t_dir+ t_name+temp
                if not os.path.exists(temp_path):       
                    t_ver=t_name+temp
                    break

        for i in file_list:
            des_path=i.replace("\\","/")
            t_list.append(unicode(des_path).replace(des_dir+"/"+t_name+"/", t_dir+"/"+t_ver+"/"))

        return t_list
    
    def move_same_file_list(self, sou_path, des_dir, is_file, t_time, is_history_with_datetime, is_move_to_history_add_version):

        if is_file:
            t_des_path=des_dir+"/"+os.path.basename(unicode(com_replace_path(sou_path)))
            if os.path.exists(t_des_path):
                self.move_to_history([t_des_path], t_time, is_history_with_datetime, is_move_to_history_add_version, des_dir, True)

        else:
            t_list    = []
            temp_list = ct.file().get_file_with_walk_folder(sou_path)
            for i in temp_list:
                i          = i.replace("\\","/")
                t_des_path = unicode(i).replace(os.path.dirname(unicode(sou_path))+"/", des_dir+"/")
                if os.path.exists(t_des_path): 
                    t_list.append(t_des_path)

            self.move_to_history(t_list, t_time, is_history_with_datetime, is_move_to_history_add_version, des_dir, False, os.path.basename(unicode(com_replace_path(sou_path))))

    def move_all_rule_file_list(self, des_dir, rule_list, t_time, is_history_with_datetime, is_move_to_history_add_version):

        re_list=self.change_to_regexp_list(rule_list)
        t_list= ct.file().get_path_list(des_dir, re_list)
        for i in t_list:
            if os.path.isfile(unicode(i)):
                self.move_to_history([i], t_time, is_history_with_datetime, is_move_to_history_add_version, des_dir, True)
            else:
                if unicode(os.path.basename(com_replace_path(i))).lower()=="history":
                    continue
                temp_list=ct.file().get_file_with_walk_folder(i)

                self.move_to_history(temp_list, t_time, is_history_with_datetime, is_move_to_history_add_version, des_dir, False, os.path.basename(unicode(com_replace_path(i))))



            
    def move_to_history(self, move_file_list, t_time, is_history_with_datetime, is_move_to_history_add_version, des_dir, is_file, t_name=""):

        if type(move_file_list)!=list:
            return
        if is_history_with_datetime:
            t_time=t_time+"/"
        else:
            t_time=""
        
        if is_file: #文件

            for sou_file in move_file_list:
                sou_file=sou_file.replace("\\","/")    
                des_path=des_dir+"/history/"+t_time
                des_filename=os.path.basename(com_replace_path(sou_file))
                des_file=des_path+des_filename
                if os.path.exists(des_path)==False:
                    os.makedirs(des_path)
            
                if is_move_to_history_add_version:
                    des_file=self.get_version_file(des_file)   

                shutil.move(sou_file, des_file)

        else: #目录
            

            if is_move_to_history_add_version:

                #new_list=move_file_list 


                new_list=self.get_version_folder(move_file_list, des_dir+"/history/"+t_time, des_dir, t_name)
                

                for i in range(len(new_list)):

                    if os.path.exists(os.path.dirname(new_list[i]))==False:
                        os.makedirs(os.path.dirname(new_list[i]))   
                    
                    shutil.move(move_file_list[i], new_list[i])                    
            else:

                for sou_file in move_file_list:
                    des_file=unicode(sou_file).replace(des_dir+"/", des_dir+"/history/"+t_time)
                    if os.path.exists(os.path.dirname(des_file))==False:
                        os.makedirs(os.path.dirname(des_file))   
                    shutil.move(sou_file, des_file)
                
            self.clear_empty_folder(move_file_list, des_dir)  
    def copy_tree(self, src, dst, symlinks = False, ignore = None):
        if not os.path.exists(dst):
            os.makedirs(dst)
            shutil.copystat(src, dst)
        lst = os.listdir(src)
        if ignore:
            excl = ignore(src, lst)
            lst = [x for x in lst if x not in excl]
        for item in lst:
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if symlinks and os.path.islink(s):
                if os.path.lexists(d):
                    os.remove(d)
                os.symlink(os.readlink(s), d)
                try:
                    st = os.lstat(s)
                    mode = stat.S_IMODE(st.st_mode)
                    os.lchmod(d, mode)
                except:
                    pass # lchmod not available
            elif os.path.isdir(s):
                self.copy_tree(s, d, symlinks, ignore)
            else:
                ct.file().copy_file(s, d)    
    def file_get_thumbnail(self, sou_file_path, work_tab_id):
        try:
            thumbnail_path = ct.com().get_tmp_path()+"/"+ct.com().uuid()+"_temp.jpg"
            ct.mov().get_mov_thumbnail(sou_file_path, thumbnail_path)
            if thumbnail_path !=False and thumbnail_path !='' and os.path.exists(thumbnail_path):
                self.class_shot_work.init_with_id([work_tab_id])
                t_res=self.class_shot_work.set_image("task.image", thumbnail_path)#不返回False就是正确的          
                try:
                    os.remove(thumbnail_path)
                except:
                    pass
                return  t_res
        except:
            return False
        return True 
    def clear_empty_folder(self, file_path_list, des_dir):

        if type(file_path_list)!=list or len(file_path_list)==0:
            return
        for s in os.listdir(des_dir):
            new_path=des_dir+"/"+s
            if  os.path.isdir(new_path):
                if s == "." or s == ".." or unicode(s).lower()=="history":
                    continue
                for i in file_path_list:
                    i=i.replace("\\","/")
                    if unicode(i).find(new_path+"/")!=-1:
                        t_list=ct.file().get_file_with_walk_folder(new_path)
                        if len(t_list)==0:
                            shutil.rmtree(new_path)
                            break    
    def change_to_regexp_list(self, file_rule_list):
        t_list=[]
        if isinstance(file_rule_list,list):
            for rule in file_rule_list:
                t_list.append(str(rule).strip().replace("#", "[0-9]").replace("?","[a-zA-Z]"))
            return t_list  
        
        
    def get_folder_des_list(self, sou_dir, des_dir):
        t_list=ct.file().get_file_with_walk_folder(sou_dir)
        t_des_file_list=[]
        for i in t_list:
            temp=i.replace("\\","/")
            t_des_file_list.append(unicode(temp).replace(sou_dir+"/", des_dir+"/"))
        return t_des_file_list
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = collating_file()
    sys.exit( app.exec_() )