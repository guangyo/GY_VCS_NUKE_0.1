# -*- coding: utf-8 -*-
"""
    Author:    黄骁颖
    Purpose:   批量打包
    Created:   2018-04-28
"""


import os
import sys
import shutil
G_base_path = os.path.dirname( os.path.dirname( os.path.dirname( __file__.replace("\\","/") ) ) )

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
from   com_widget        import *

class packing_thread(QThread):
    m_signal_state    = Signal(int, int,str)
    m_signal_complete = Signal(int,str)
    m_signal_running  = Signal(int,str)
    
    STATUS_ERROR   = 0   #失败
    STATUS_SUCCESS = 1   #成功
    STATUS_PASS    = 2   #NULL 跳过
    
    RUN_ABNORMAL  = 0  #整体出错
    RUN_SUCCESS   = 1  #全部完成
    RUN_ERROR     = 2  #有错
    
    
    def __init__(self, a_data, a_parent=None):
        super(packing_thread, self).__init__(a_parent)

        self.m_all_task_info          = a_data["task_info"]
        self.m_is_copy_all_file_ = a_data["is_copy_all_file"]
        self.m_is_save_folder    = a_data["is_save_folder"]
        self.m_des_dir           = a_data["des_dir"]
        

    #---路径，规则
    def __get_task_info(self, a_task_module, a_link_id, a_filebox_id):
        a_task_module.init_with_id(a_link_id)
        filebox_data = a_task_module.get_filebox_with_filebox_id(a_filebox_id)  

        if type(filebox_data) == dict:
            t_rule_list = filebox_data["rule"]
            t_path = filebox_data["path"]    
            re_list = self.change_to_regexp_list(t_rule_list)
        return t_path,re_list
    
        
        #'<br><span style="color:#FF0000;">'+ u"Error:创建镜头号失败:------>%s\n"%(t_shot_name)+ '</span>'
    def do_work(self):
        success = True  #---全部成功

        for i in self.m_all_task_info:
            t_row          = i["row_index"]
            t_task_module  = i["class_name"]
            t_link_id      = i["link_id"]
            t_filebox_id   = i["filebox_id"]
            t_entity_name  = i["entity_name"]
            try:
                t_path,t_rule_list = self.__get_task_info(t_task_module,t_link_id,t_filebox_id)
            except Exception,e:
                success = False
                self.m_signal_running.emit(t_row,u"获取文件框信息失败")
                self.m_signal_state.emit(t_row,self.STATUS_ERROR,'<span style="color:#FF0000;">'+u"获取文件框信息失败"+'</span>')

                continue 
            

            if os.path.exists(t_path):
                t_list =  ct.file().get_path_list(t_path, t_rule_list)  
                t_name_list = ""
                t_file_list = []
                t_sou_path = []
                

                if isinstance(t_list, list) and t_list != []:
                    #--------过滤
                    for t_file in t_list:
                        if os.path.isdir(unicode(t_file)) and unicode(os.path.basename(t_file)).lower() == "history":
                            continue 
                        if os.path.basename(t_file) == "Thumbs.db":
                            continue                          
                        t_file_list.append(t_file)
                        a_file_name = os.path.basename(t_file)
                        a_file_name.split()
                        t_name_list += a_file_name+","  
                    if len(t_file_list) == 0:
                        self.m_signal_running.emit(t_row,u"NULL")
                        self.m_signal_state.emit(t_row,self.STATUS_PASS,'<span style="color:#FF0000;">'+u"文件列表为空"+'</span>')
                        continue                    
                    
                    
                    #---判断是全部文件或者最大文件
                    if not self.m_is_copy_all_file_ :
                        t_sou_path.append(self.sorted(t_file_list, True)[0])
                        t_name_list =  os.path.basename(t_sou_path[0]).replace(",","")
                    else:
                        t_sou_path = t_file_list
                    self.m_signal_running.emit(t_row,t_name_list)                     
                    
                    #-------复制文件
                    try:
                        for t_file in t_sou_path:
                            #---保持目录结构
                            if self.m_is_save_folder:
                                t_new_path = (self.m_des_dir + os.path.splitdrive(os.path.dirname(t_file))[1]).replace("\\", "/")
                                if not os.path.exists(t_new_path):
                                    os.makedirs(t_new_path)
                                if os.path.isdir(t_file):
                                    des_path = t_new_path + "/" +  t_file.replace("\\", "/").split("/")[-1]

                                    self.copy_file(t_file,des_path)
                                else: 
                                    #===============骁颖==2018.06.15=========================
                                    #shutil.copy(t_file, t_new_path + "/" +  t_file.replace("\\", "/").split("/")[-1])
                                    
                                    ct.file().copy_file(t_file, t_new_path + "/" +  t_file.replace("\\", "/").split("/")[-1]) 
                                    #===============骁颖==2018.06.15=========================
                                    
                                    
                            #--不保持目录结构
                            else:
                                if os.path.isdir(t_file):
                                    des_path = self.m_des_dir + "/" + t_file.replace("\\", "/").split("/")[-1] 
                                    self.copy_file(t_file,des_path)
                                else:
                                    #===============骁颖==2018.06.15===================== 
                                    #shutil.copy(t_file, self.m_des_dir + "/" + t_file.replace("\\", "/").split("/")[-1])
                                    ct.file().copy_file(t_file, self.m_des_dir + "/" + t_file.replace("\\", "/").split("/")[-1]) 
                                    #===============骁颖==2018.06.15===================== 
                        self.m_signal_state.emit(t_row,self.STATUS_SUCCESS,"")
                    except Exception,e:
                        success = False
                        self.m_signal_state.emit(t_row,self.STATUS_ERROR,'<span style="color:#FF0000;">'+u"复制文件失败"+'</span>') 
                        continue
                    
                #----文件列表为空   
                else:
                    self.m_signal_running.emit(t_row,u"NULL")
                    self.m_signal_state.emit(t_row,self.STATUS_PASS,'<span style="color:#FF0000;">'+u"文件列表为空"+'</span>')
                    continue    
            #----目录不存在  
            else:
                self.m_signal_running.emit(t_row,u"NULL")
                self.m_signal_state.emit(t_row,self.STATUS_PASS,'<span style="color:#FF0000;">'+u"目录不存在"+'</span>') 
        return success
    
    #排序
    def sorted(self, lis, is_reverse=False):  
        lists=list(lis)
        count=len(lists)
        for i in range(0,count):
            for j in range(i+1,count):
                if is_reverse:
                    if unicode(lists[i]).lower() < unicode( lists[j]).lower():
                        lists[i],lists[j]=lists[j],lists[i]
                else:
                    if unicode(lists[i]).lower() > unicode( lists[j]).lower():
                        lists[i],lists[j]=lists[j],lists[i]		
        return lists
    
    def copy_file(self,t_path, des_path):
        if not os.path.exists(des_path):
            os.makedirs(des_path)
        t_file_list = ct.file().get_path_list(t_path,["*"])
        for t_file in t_file_list:
            if os.path.isfile(t_file):
                #===============骁颖==2018.06.15===================== 
                
                #shutil.copy(t_file, des_path)    
                ct.file().copy_file(t_file, des_path)    
                #===============骁颖==2018.06.15===================== 
            else:
                self.copy_file(t_file,(des_path+"/"+os.path.basename(t_file)))

            
    def run(self):     
        try:
            info = self.do_work() 
            if info == True:
                self.m_signal_complete.emit(self.RUN_SUCCESS,u"复制完成")
            else:
                self.m_signal_complete.emit(self.RUN_ERROR,u"请查看状态列")
        except Exception,e:
            self.m_signal_complete.emit(self.RUN_ABNORMAL,str(unicode(e)))
            
    def change_to_regexp_list(self, file_rule_list):
        t_list = []
        if isinstance(file_rule_list, list):
            for rule in file_rule_list:
                t_list.append(unicode(rule).strip().replace("#", "[0-9]").replace("?", "[a-zA-Z]"))
            return t_list

                
class pack_file_widget(widget):
    COL_LINK      = 0
    COL_FILE_NAME = 1
    COL_STATE     = 2
    
    INDEX_MAX = 0
    INDEX_ALL = 1
    
    COL_DATA = 0
    ROLE_LINK_ID  = 32           
    ROLE_PATH     = 34
    ROLE_RULE     = 33
    ROLE_TOOLTIP  = 35
    def __init__(self):
        super(pack_file_widget, self).__init__()
        self.__ui__()
        self.set_Cgtw()


    def set_Cgtw(self):
        self.set_UI()
        try:
            self.m_tw = tw()
            self.m_database = self.m_tw.sys().get_sys_database()
            self.m_id_list = self.m_tw.sys().get_sys_id()
            self.m_module = self.m_tw.sys().get_sys_module()
            self.m_module_type = self.m_tw.sys().get_sys_module_type()

            self.m_filebox_id = self.m_tw.sys()._get_sys_key("filebox_id")
            self.m_pipeline_id = self.m_tw.sys()._get_sys_key("pipeline_id")
            
            if self.m_module_type != "task":
                message().error(u"只允许在制作模块使用")
            self.m_task_module = self.m_tw.task_module(self.m_database, self.m_module)

            #---过滤
            task_id_list =  self.m_task_module.get_with_filter(["task.id"],[["task.set_pipeline_id","=",self.m_pipeline_id],"and",["task.id","in",self.m_id_list]])
            new_list = []
            for i in task_id_list:
                new_list.append(i["task.id"])
            self.m_id_list = new_list

            if type(self.m_id_list)!=list or len(self.m_id_list)==0:
                message().error(u"请选择需要复制的任务,或选择的任务有误!")            
            
            
            t_timer = QTimer(self)
            t_timer.timeout.connect(self.scanning)
            t_timer.setSingleShot(True)
            t_timer.start(200)
            
        except Exception, e:
            message().error(u"读取数据库失败\n" + str(e))

    def set_UI(self):
        self.setMinimumSize(800, 600)
        self.m_title_label.setText(u"批量打包")
        t_lay_content = QHBoxLayout()
        
        #---tablewidget
        self.m_tablewidget_sou = QTableWidget()
        self.m_tablewidget_sou.setColumnCount(3)
        self.m_tablewidget_sou.setHorizontalHeaderLabels(["Link", "文件名", "状态"])
        self.m_tablewidget_sou.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.m_tablewidget_sou.horizontalHeader().setHighlightSections(True)
        self.m_tablewidget_sou.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.m_tablewidget_sou.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.m_tablewidget_sou.horizontalHeader().setStretchLastSection(True)
        self.resizeEvent = self.resizeEvent
        self.m_tablewidget_sou.verticalHeader().setVisible(False)
        self.m_tablewidget_sou.setShowGrid(False)

        t_lay_bottom = QHBoxLayout()
        #---frame
        t_lay_button_left = QHBoxLayout()
        self.frame = QFrame()
        self.frame.setMinimumSize(QSize(501, 81))
        self.frame.setMaximumSize(QSize(501, 81))        
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)            
        
        #--1
        self.m_combobox_check_file = QComboBox(self.frame)
        self.m_combobox_check_file.setView(QListView())
        self.m_combobox_check_file.addItem(u"最大版本")
        self.m_combobox_check_file.addItem(u"所有文件")
        self.m_combobox_check_file.setGeometry(QRect(80, 10, 121, 22))
        
        #---2
        self.m_checkbox_save_folder = QCheckBox(self.frame)
        self.m_checkbox_save_folder.setGeometry(QRect(394, 14, 21, 16))
        
        #---确定按钮
        self.m_button_submit = QPushButton(u"确定")
        self.m_button_submit.setMinimumSize(QSize(81, 81))
        self.m_button_submit.setMaximumSize(QSize(81, 81))

        self.m_button_submit.setObjectName("m_button_submit")
        self.m_button_submit.clicked.connect(self.slt_submit)
        #---3
        self.m_line_text  = QLineEdit(self.frame)
        self.m_line_text.setGeometry(QRect(80, 50, 301, 20))
        self.m_line_text.setObjectName("m_line_text")
        self.m_line_text.setPlaceholderText(u"请选择要存放的目录")
        self.m_line_text.setMinimumHeight(23)

        #---4
        self.m_button_files = QPushButton(self.frame)  
        self.m_button_files.setText("...")
        self.m_button_files.setObjectName("m_button_files")
        self.m_button_files.clicked.connect(self.slt_set_des_path)
        self.m_button_files.setGeometry(QRect(390, 50, 31, 23))
        
        #--5
        self.m_lable_1  = QLabel(self.frame)
        self.m_lable_1.setGeometry(QRect(18, 14, 61, 16))
        self.m_lable_1.setText(u"文件类型:")
        self.m_lable_1.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.m_lable_2  = QLabel(self.frame)
        self.m_lable_2.setGeometry(QRect(300, 14, 91, 16))
        self.m_lable_2.setText(u"保持目录结构:")
        self.m_lable_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.m_lable_3  = QLabel(self.frame)
        self.m_lable_3.setGeometry(QRect(18, 54, 61, 16))
        self.m_lable_3.setText(u"路径:")
        self.m_lable_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        
  
        t_lay_content.addWidget(self.m_tablewidget_sou)
        t_lay_button_left.addWidget(self.frame)
        t_lay_button_left.addStretch()
        
       
        t_lay_button_left.addWidget(self.m_button_submit)       
        t_lay_bottom.addLayout(t_lay_button_left)
        self.m_tablewidget_sou.itemClicked.connect(self.slt_show_tooltip)
        self.parent_lay.addLayout(t_lay_content)
        self.parent_lay.addLayout(t_lay_bottom)
        self.setLayout(t_lay_content)
        self.set_style()
        self.show()

    def slt_set_des_path(self):
        t_des_dir = QFileDialog.getExistingDirectory(self, u"请选择目录", "",QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        t_des_dir = unicode(t_des_dir)
        if t_des_dir.strip().lower() == "":
            return
        self.m_line_text.setText(t_des_dir)


    def set_style(self):
        qApp.setStyleSheet(unicode("QToolTip{background-color:#FFFFFF;color:#666666;border:1px solid #E9E9E9;border-radius:4px;padding:2px;}"
                                            "QTableView,QTableWidget{border:1px solid #E9E9E9;color:#666666;border-radius:4px;background:white;outline:0px;}"
                                            "QTableWidget:item{border:0px;padding-left:5px;border-bottom:1px solid #E9E9E9;}"
                                            "QTableView::item:selected:!active{background-color:#E9E9E9;border-bottom:1px solid #FFFFFF;}"
                                            "QTableView::item:selected:active{background-color:#E9E9E9;border-bottom:1px solid #FFFFFF;}"
                                            "QHeaderView{color:#666666;min-height:32px;}"
                                            "QHeaderView::section{background-color:white;padding-left:5px;border:0;border-bottom:1px solid #E9E9E9;}", encoding='utf8'))
        #self.m_tablewidget_sou.setStyleSheet()
        self.m_combobox_check_file.setFixedSize(100,25)

        
        self.m_button_submit.setStyleSheet("QPushButton{background-color:#108ee9;color:#FFFFFF;font-size:12px;border-radius:4px;}"
                                         "QPushButton:hover{background-color:#1083E0; border-radius:4px; font-size:12px; color:#FFFFFF;}"
                                         "#m_button_submit{margin-top:10px}")
        self.m_button_files.setStyleSheet("#m_button_files{ border: 1px solid E9E9E9;border-radius:4px; ;color:666666;font-size:12px;; background-color:#FFFFFF}")
        self.m_combobox_check_file.setStyleSheet("QComboBox{  ;font-size:12px;border-radius:4px; }")
        self.m_line_text.setStyleSheet("QLineEdit:hover{border: 1px solid E9E9E9;border-radius: 4px;background-color:666666;color:cccccc;}"
                                       "QLineEdit{border: 1px solid E9E9E9;border-radius: 4px;background-color:666666;}")
        
    
                                       #"QLineEdit{color:cccccc}")
        
        
    def scanning(self):
        try:
            self.m_tablewidget_sou.setRowCount(0)
            t_task_dic =   self.m_tw.link_entity().get_entity_name(self.m_database, self.m_id_list)
            for i in t_task_dic :
                t_entity_name = i["entity_name"]
                t_link_id     = i["link_id"]
                t_rowCount = self.m_tablewidget_sou.rowCount()
                self.m_tablewidget_sou.insertRow(t_rowCount)            
                self.m_tablewidget_sou.setItem(t_rowCount, self.COL_LINK, QTableWidgetItem(t_entity_name))
                self.m_tablewidget_sou.item(t_rowCount, self.COL_DATA).setData(self.ROLE_LINK_ID,t_link_id)
        except Exception,e:
            message().error(u"获取link_entity失败")
            




    #延迟
    def delay(self, a_msec):
        die_time=QTime.currentTime().addMSecs(a_msec)
        while QTime.currentTime()<die_time:
            QCoreApplication.processEvents(QEventLoop.AllEvents, 100)
            

    def resizeEvent(self, event):
        self.m_tablewidget_sou.setColumnWidth(self.COL_LINK, int(self.m_tablewidget_sou.size().width() * 0.35))
        self.m_tablewidget_sou.setColumnWidth(self.COL_FILE_NAME, int(self.m_tablewidget_sou.size().width() * 0.54))
        self.m_tablewidget_sou.setColumnWidth(self.COL_STATE, int(self.m_tablewidget_sou.size().width() * 0.10))

    def slt_show_tooltip(self, a_item):
        t_row          = self.m_tablewidget_sou.row(a_item)
        t_tooltip_data = self.m_tablewidget_sou.item(int(t_row), self.COL_DATA).data(self.ROLE_TOOLTIP)
        QToolTip.showText(QCursor.pos(), t_tooltip_data)

    def slt_submit(self):
        t_des_dir = self.m_line_text.text()
        if t_des_dir == "":
            message().error(u"请选择要存放的目录",False)
            return
        if not os.path.exists(t_des_dir):
            message().error(u"存放路径不存在",False)
            return 


        try:
            self.m_button_submit.setEnabled(False)
            t_is_copy_all_file = self.m_combobox_check_file.currentIndex()
            t_is_save_folder   = self.m_checkbox_save_folder.isChecked()
            
            t_all_task_info = []
            t_rows = self.m_tablewidget_sou.rowCount()
            for rows_index in range(t_rows):
                t_link_id =  self.m_tablewidget_sou.item(rows_index, self.COL_DATA).data(self.ROLE_LINK_ID)
                t_entity_name = self.m_tablewidget_sou.item(rows_index, self.COL_LINK).text()
                t_all_task_info.append({"row_index":rows_index, "class_name":self.m_task_module, "link_id":t_link_id, "filebox_id":self.m_filebox_id,"entity_name":t_entity_name})

                
            t_data ={"task_info":t_all_task_info,"is_save_folder":t_is_save_folder,"is_copy_all_file":t_is_copy_all_file,"des_dir":t_des_dir}
            self.t_thread = packing_thread(t_data)
            self.t_thread.m_signal_state.connect(self.slt_state)
            self.t_thread.m_signal_running.connect(self.slt_running_change)
            self.t_thread.m_signal_complete.connect(self.slt_complete)
            self.t_thread.start()


        except Exception, e:
            message().error(u"复制错误!!\n" +str(e), False)
            self.m_button_submit.setEnabled(True)



    def slt_running_change(self,a_row, a_file_name):
        self.m_tablewidget_sou.setItem(a_row,self.COL_FILE_NAME,QTableWidgetItem(u"%s"%a_file_name))
        self.m_tablewidget_sou.setItem(a_row,self.COL_STATE,QTableWidgetItem(u"正在上传"))
        self.m_tablewidget_sou.setCurrentItem(self.m_tablewidget_sou.item(a_row, 0))
        
    def slt_state(self, a_row, a_state,a_error_info ):
        if a_state == 1:
            t_item = QTableWidgetItem(u"成功")
            t_item.setTextColor(Qt.green)
            self.m_tablewidget_sou.setItem(a_row,self.COL_STATE,t_item) 
            self.m_tablewidget_sou.item(a_row, self.COL_DATA).setData(self.ROLE_TOOLTIP,u"成功")
        elif a_state == 0:
            self.m_tablewidget_sou.item(a_row, self.COL_STATE).setText(u"失败")
            self.m_tablewidget_sou.item(a_row, self.COL_STATE).setTextColor(Qt.red)
            self.m_tablewidget_sou.item(a_row, self.COL_DATA).setData(self.ROLE_TOOLTIP,a_error_info)
        elif a_state == 2:
            self.m_tablewidget_sou.item(a_row, self.COL_STATE).setText(u"跳过")
            self.m_tablewidget_sou.item(a_row, self.COL_DATA).setData(self.ROLE_TOOLTIP,a_error_info)
            
            
            
    def slt_complete(self, a_state, a_info):
        if a_state == 1:
            message().info(a_info,False)  
            self.m_button_submit.setEnabled(True)
        else:
            self.m_button_submit.setEnabled(True)
            message().error(a_info,False)            
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = pack_file_widget()
    win.show()
    sys.exit(app.exec_())