#coding:utf8
#Author  :王晨飞
#Time    :2017-12-29
#Describe:New finishing
#         子线程
#         info,task均可使用,去除History
#         CgTeamWork_V5整理
import os 
import re
import sys
import time
import json
import shutil
import datetime
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
from   com_work_log      import *
from   com_message_box   import *
from   cgtw              import *
from   com_function      import * 
from   com_widget        import *
class copy_file_widget(widget):
    def __init__(self):
        super(copy_file_widget, self).__init__()
	self.__ui__()
        self.set_Cgtw()
    def set_Cgtw(self):
	self.set_UI()
        try:
            self.m_tw            = tw()
            self.m_database      = self.m_tw.sys().get_sys_database()
            self.m_id_list       = self.m_tw.sys().get_sys_id()
            self.k_log_show      = self.m_tw.sys().get_argv_key("is_show_log")
            self.m_filebox_class = self.m_tw.filebox(self.m_database)
            self.m_module        = self.m_tw.sys().get_sys_module()
	    self.m_module_type   = self.m_tw.sys().get_sys_module_type()
            if type(self.m_id_list)!=list or len(self.m_id_list)==0:
                message().error(u"请选择需要复制的任务!")
		
	    if self.m_module_type == "info":
		self.m_module_class = self.m_tw.info_module(self.m_database, self.m_module)
	    else:
		self.m_module_class = self.m_tw.task_module(self.m_database, self.m_module, self.m_id_list)
		t_data_list         = self.m_module_class.get([self.m_module+".id"])
		self.m_id_list      = []
		for t_data in t_data_list:
		    self.m_id_list.append( t_data[self.m_module+".id"] )
		self.m_id_list = list(set(self.m_id_list))
		self.m_module_class = self.m_tw.info_module(self.m_database, self.m_module)
		
	    self.m_pipeline_class = self.m_tw.pipeline( self.m_database )
	    self.m_pipeline_list  = self.m_pipeline_class.get_with_module(self.m_module,["name","#id"])
	    if type(self.m_pipeline_list) != list or len(self.m_pipeline_list) == 0:
		message().error( u"取制作阶段列表失败, 请确认是否有配置制作阶段!" )
	    for pipeline in self.m_pipeline_list:
		t_filebox_list = self.m_filebox_class.get_with_pipeline_id(pipeline["id"],self.m_module)
		if type(t_filebox_list)==list and len(t_filebox_list)>0:
		    pipeline_item = QTreeWidgetItem( self.treeWidget_sou )
		    pipeline_item.setText(0, pipeline["name"])
		    for i in t_filebox_list:
			item = QTreeWidgetItem(pipeline_item)
			item.setText(0, unicode(i["title"]))
			item.setData(0, 32, i["id"])
		    pipeline_item = QTreeWidgetItem( self.treeWidget_des )
		    pipeline_item.setText(0, pipeline["name"])
		    for i in t_filebox_list:
			item = QTreeWidgetItem(pipeline_item)
			item.setText(0, unicode(i["title"]))
			item.setData(0, 32, i["id"])
        except Exception,e:
	    message().error(u"读取数据库失败")
	self.set_style()
        self.show()
	self.m_work_log = plugin_log_widget()
        if str(self.k_log_show).lower()=="y":
            t_x= self.pos().x()
            t_y= self.pos().y()
            self.m_work_log.move( t_x+405,t_y )
            self.m_work_log.setMinimumSize(300,500)
            self.m_work_log.show()
            self.move( t_x-150,t_y )
    def set_UI(self):
        self.setMinimumSize(350,500)
        self.m_title_label.setText(u"复制文件")
	self.treeWidget_sou = QTreeWidget()
	self.treeWidget_sou.setHeaderLabel(u"源路径：阶段/文件框")
	self.tree_lable     = QLabel()
	self.tree_lable.setText(" => ")
	self.treeWidget_des = QTreeWidget()
	self.treeWidget_des.setHeaderLabel(u"目标路径：阶段/文件框")
	lay_center_toolbar  = QHBoxLayout()
	lay_center_toolbar.addWidget(self.treeWidget_sou)
	lay_center_toolbar.addWidget(self.tree_lable)
	lay_center_toolbar.addWidget(self.treeWidget_des)
	self.parent_lay.addLayout(lay_center_toolbar)
	self.m_radio_max = QRadioButton()
	self.m_radio_max.setText(u"最大版本")
	self.m_radio_max.setChecked(True)
	self.m_radio_all = QRadioButton()
	self.m_radio_all.setText(u"所有文件")
	self.m_copy_button = QPushButton()
	self.m_copy_button.setText(u"复制")	
	lay_bottom_toolbar  = QHBoxLayout()
	lay_bottom_toolbar.addWidget(self.m_radio_max)
	lay_bottom_toolbar.addWidget(self.m_radio_all)
	lay_bottom_toolbar.addStretch()
	lay_bottom_toolbar.addWidget(self.m_copy_button)
	lay_bottom_toolbar.setContentsMargins(0,8,0,0)
	self.parent_lay.addLayout(lay_bottom_toolbar)
	self.m_copy_button.clicked.connect(self.slt_copy)
	self.m_close_button.clicked.connect(self.slt_close)
    def set_style(self):
        self.m_copy_button.setFixedSize(60,28)
        self.m_copy_button.setStyleSheet("QPushButton{background-color:#108ee9;color:#FFFFFF;font-size:12px;border-radius:4px;}"
	                                 "QPushButton:hover{background-color:#1083E0; border-radius:4px; font-size:12px; color:#FFFFFF;}"
	                                 )    
	self.treeWidget_sou.setStyleSheet("QTreeWidget{border-radius:4px;border:1px solid #E5E6E7;}")
	self.tree_lable.setStyleSheet("QLabel{color:#666666;font-size:12px;}")
	self.treeWidget_des.setStyleSheet("QTreeWidget{border-radius:4px;border:1px solid #E5E6E7;}")
	self.m_radio_all.setStyleSheet("QRadioButton{color:#666666;}")
	self.m_radio_max.setStyleSheet("QRadioButton{color:#666666;}")	
    def set_Thread(self, a_data, a_queue, a_signal, a_event):
	thread_sou_id_list   = a_data[0]
	thread_des_id_list   = a_data[1]
	thread_task_class    = a_data[2]
	thread_sou_folder_id = a_data[3]
	thread_des_folder_id = a_data[4]
	thread_tw_class      = a_data[5]
	t_time               = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
	t_copy_fail          = ""
	for i in range(len(thread_sou_id_list)):
	    t_sou_id      = thread_sou_id_list[i]
	    t_des_id      = thread_des_id_list[i]
	    t_submit_list = []
	    try:
		thread_task_class.init_with_id(t_sou_id)
		filebox_data_sou = thread_task_class.get_filebox_with_filebox_id( thread_sou_folder_id )
		thread_task_class.init_with_id(t_des_id)
		filebox_data_des = thread_task_class.get_filebox_with_filebox_id( thread_des_folder_id )
		if type(filebox_data_sou)!=dict and type(filebox_data_des)!=dict:
		    return
		t_rule_list_sou = filebox_data_sou['rule']
		t_path_sou      = filebox_data_sou['path']
		t_path_des      = filebox_data_des['path']
		re_list_sou     = com_str_to_rule("|".join(t_rule_list_sou),True)
		if self.m_radio_all.isChecked():
		    t_list=ct.file().get_path_list(t_path_sou, re_list_sou)
		    for i in t_list:
			temp_bool = False
			if os.path.isdir(unicode(i)) and unicode(os.path.basename(com_replace_path(i))).lower()=="history":
			    temp_bool = True 
			if unicode(os.path.basename(com_replace_path(i))).lower().find(".ini")==1 or unicode(os.path.basename(com_replace_path(i))).lower().find(".db")==1:
			    temp_bool = True 
			if temp_bool != True:
			    t_copy_fail = com_copy( [i], t_path_des, a_fail_str = t_copy_fail, a_time=t_time, a_is_folder_son=True, a_work_log_signal = a_signal)
			    a_signal.emit("log", u"Info:拷贝文件:%s------------%s"%(i, unicode(t_path_des+"/"+os.path.basename(com_replace_path(i)))), True)
			    t_submit_list.append(t_path_des +"/"+ os.path.basename(com_replace_path(i)))
		else:
		    t_sou=ct.file().get_path(t_path_sou, re_list_sou, True, True)
		    if unicode(t_sou).lower().strip()!="":
			t_copy_fail = com_copy( [t_sou], t_path_des, a_fail_str = t_copy_fail, a_time=t_time, a_is_folder_son=True, a_work_log_signal = a_signal)
			t_submit_list.append(t_path_des +"/"+ os.path.basename(com_replace_path(t_sou)))
			a_signal.emit("log", u"Info:拷贝文件:%s------------%s"%(t_sou, unicode(t_path_des+"/"+os.path.basename(com_replace_path(t_sou)))), True)
		#----------------
		t_is_submit = thread_tw_class.sys().get_argv_key("is_submit")
		if str( t_is_submit ).lower().strip()=="y":
		    t_file_path_list = []
		    t_path_list      = []
		    for i in t_submit_list:
			t_path_list.append(i.replace("\\","/"))
			if os.path.isdir(i):
			    for n in ct.file().get_file_with_walk_folder(i):
				t_file_path_list.append(n.replace("\\","/"))
			else:
			    t_file_path_list.append(i.replace("\\","/"))
			
		    thread_task_class.submit(t_file_path_list,"",t_path_list)
		#--------------------
	    except Exception,e:
		print e
		t_copy_fail= t_copy_fail + u"ID:%s---读取数据失败!\n"%(t_sou_id)
	if t_copy_fail=="":
	    a_signal.emit("log", u"Success:完成",True)
	    a_signal.emit("info", u"完成", True)
	    a_event.wait()
	else:
	    a_signal.emit("log", u"Error:以下复制失败:\n"+t_copy_fail,True )
	    a_signal.emit("error", u"以下复制失败:\n"+t_copy_fail, False)
	    a_event.wait()
	    a_signal.emit("QPushButton","True", True)
    #----------------------------------------slot-------------------------------------	    
    def slt_add_log(self, a_data):
	try:
	    if str(self.k_log_show).lower()=="y":
		self.m_work_log.slt_add_log( a_data )
	except:
	    pass
    def slt_copy(self):
	self.m_copy_button.setEnabled(False)
	t_sou = self.treeWidget_sou.currentItem()
	t_des = self.treeWidget_des.currentItem()
	if not t_sou is None:
	    t_sou_parent = t_sou.parent()
	    if t_sou_parent is None:
		self.slt_add_log( u"Error:请选择源文件筐")
		message().error(u"请选择源文件筐!",False)
		self.m_copy_button.setEnabled(True)
		return
	    else:
		t_sou_id =  t_sou.data(0,32)
		t_sou_item_name = t_sou.parent().text(0)
	else:
	    self.slt_add_log( u"Error:请选择源文件筐")
	    message().error(u"请选择源文件筐!",False)
	    self.m_copy_button.setEnabled(True)
	    return	    
	if not t_des is None:
	    t_des_parent = t_des.parent()
	    if t_des_parent is None:
		self.slt_add_log( u"Error:请选择目标文件筐")
		message().error(u"请选择目标文件筐!",False)
		self.m_copy_button.setEnabled(True)
		return
	    else:
		t_des_id =  t_des.data(0,32)
		t_des_item_name = t_des.parent().text(0)
	else:
	    self.slt_add_log( u"Error:请选择目标文件筐")
	    message().error(u"请选择目标文件筐!",False)
	    self.m_copy_button.setEnabled(True)
	    return
	#--------------------------
	self.m_module_class = self.m_tw.task_module(self.m_database, self.m_module)
	t_sou_id_list       = []
	t_des_id_list       = []
	try:
	    self.m_module_class.init_with_filter([ [self.m_module + ".id", "in", self.m_id_list ], "and", ["task.pipeline", "=", t_sou_item_name ]])
	    temp_sou_data   = self.m_module_class.get(["task.id", self.m_module + ".id"])
	    self.m_module_class.init_with_filter([ [self.m_module + ".id", "in", self.m_id_list ], "and", ["task.pipeline", "=", t_des_item_name ]])
	    temp_des_data   = self.m_module_class.get(["task.id", self.m_module + ".id"])
	    print temp_des_data
	    if len(temp_sou_data) == len(temp_des_data):
		for sou_data in temp_sou_data:
		    t_sou_id_list.append( sou_data["task.id"] )
		    for des_data in temp_des_data:
			if des_data[self.m_module + ".id"] == sou_data[self.m_module + ".id"]:
			    t_des_id_list.append( des_data["task.id"] )
	    if len(t_sou_id_list) == len(t_des_id_list) and len(t_des_id_list)>0:
		t_data = [t_sou_id_list, t_des_id_list, self.m_module_class, t_sou_id, t_des_id, self.m_tw]
		self.m_work_log.run(self.set_Thread, t_data, self.m_copy_button)	
	    else:
		print t_sou_id_list,t_des_id_list
		self.slt_add_log( u"Error:读取数据库存在错误！")
		message().error(u"读取数据库存在错误!",False)
		self.m_copy_button.setEnabled(True)
		return	
	except Exception,e:
	    self.slt_add_log( u"Error:读取数据库存在错误！")
	    message().error(u"读取数据库存在错误!",False)
	    self.m_copy_button.setEnabled(True)
	    return
    def slt_close(self):
	sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = copy_file_widget()
    sys.exit( app.exec_() )