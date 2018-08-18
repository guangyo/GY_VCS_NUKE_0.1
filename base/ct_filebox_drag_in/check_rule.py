#coding:utf-8
"""
  Author:  shiming
  Purpose: 检查命名规则,返回新的{sou_list:[], des_list:[]}
  Created: 2018-03-13
"""
import os
import sys
import traceback

#加载ct_plu库
t_base_path=unicode(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/")
t_cgtw_path = os.path.dirname( t_base_path ) + "/cgtw/"

if t_base_path not in sys.path:
    sys.path.append(t_base_path)
if not t_cgtw_path in sys.path:
    sys.path.append( t_cgtw_path )
    
try:
    from cgtw import *
    import ct_plu
    from  ct_plu.qt import * #导入QT的库
    import ct_lib
    import ct_ui
except Exception,e:
    raise Exception(traceback.format_exc())  

#更改命名规则窗口--
class Ui_modify_filename(object):
    def setupUi(self, modify_filename):
	modify_filename.setObjectName("modify_filename")
	modify_filename.resize(426, 278)
	self.verticalLayout = QVBoxLayout(modify_filename)
	self.verticalLayout.setSpacing(0)
	self.verticalLayout.setContentsMargins(5, 5, 5, 5)
	self.verticalLayout.setObjectName("verticalLayout")
	self.frame_top = QFrame(modify_filename)
	self.frame_top.setFrameShape(QFrame.StyledPanel)
	self.frame_top.setFrameShadow(QFrame.Raised)
	self.frame_top.setObjectName("frame_top")
	self.horizontalLayout_4 = QHBoxLayout(self.frame_top)
	self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
	self.horizontalLayout_4.setObjectName("horizontalLayout_4")
	self.label_image = QLabel(self.frame_top)
	self.label_image.setMinimumSize(QSize(56, 0))
	self.label_image.setMaximumSize(QSize(56, 16777215))
	self.label_image.setText("")
	self.label_image.setPixmap(QPixmap(":/icons/filebox/error.png"))
	self.label_image.setAlignment(Qt.AlignCenter)
	self.label_image.setObjectName("label_image")
	self.horizontalLayout_4.addWidget(self.label_image)
	self.verticalLayout_4 = QVBoxLayout()
	self.verticalLayout_4.setObjectName("verticalLayout_4")
	self.horizontalLayout_3 = QHBoxLayout()
	self.horizontalLayout_3.setObjectName("horizontalLayout_3")
	self.label_title = QLabel(self.frame_top)
	self.label_title.setMinimumSize(QSize(0, 21))
	self.label_title.setText("")
	self.label_title.setScaledContents(True)
	self.label_title.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
	self.label_title.setWordWrap(True)
	self.label_title.setObjectName("label_title")
	self.horizontalLayout_3.addWidget(self.label_title)
	self.pushButton_close = QPushButton(self.frame_top)
	self.pushButton_close.setMinimumSize(QSize(25, 25))
	self.pushButton_close.setMaximumSize(QSize(25, 25))
	self.pushButton_close.setText("")
	icon = QIcon()
	icon.addPixmap(QPixmap(":/icons/close.png"), QIcon.Normal, QIcon.Off)
	self.pushButton_close.setIcon(icon)
	self.pushButton_close.setFlat(True)
	self.pushButton_close.setObjectName("pushButton_close")
	self.horizontalLayout_3.addWidget(self.pushButton_close)
	self.verticalLayout_4.addLayout(self.horizontalLayout_3)
	self.label = QLabel(self.frame_top)
	self.label.setMinimumSize(QSize(0, 21))
	self.label.setMaximumSize(QSize(16777215, 30))
	self.label.setText("")
	self.label.setObjectName("label")
	self.verticalLayout_4.addWidget(self.label)
	self.horizontalLayout_4.addLayout(self.verticalLayout_4)
	self.verticalLayout.addWidget(self.frame_top)
	self.frame_bottom = QFrame(modify_filename)
	self.frame_bottom.setFrameShape(QFrame.StyledPanel)
	self.frame_bottom.setFrameShadow(QFrame.Raised)
	self.frame_bottom.setObjectName("frame_bottom")
	self.verticalLayout_2 = QVBoxLayout(self.frame_bottom)
	self.verticalLayout_2.setContentsMargins(14, 0, 14, 5)
	self.verticalLayout_2.setObjectName("verticalLayout_2")
	self.tableWidget = QTableWidget(self.frame_bottom)
	self.tableWidget.setFocusPolicy(Qt.WheelFocus)
	self.tableWidget.setObjectName("tableWidget")
	self.tableWidget.setColumnCount(0)
	self.tableWidget.setRowCount(0)
	self.verticalLayout_2.addWidget(self.tableWidget)
	self.horizontalLayout = QHBoxLayout()
	self.horizontalLayout.setObjectName("horizontalLayout")
	self.checkBox = QCheckBox(self.frame_bottom)
	self.checkBox.setObjectName("checkBox")
	self.horizontalLayout.addWidget(self.checkBox)
	spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
	self.horizontalLayout.addItem(spacerItem)
	self.pushButton_ok = QPushButton(self.frame_bottom)
	self.pushButton_ok.setMinimumSize(QSize(60, 28))
	self.pushButton_ok.setMaximumSize(QSize(60, 28))
	self.pushButton_ok.setObjectName("pushButton_ok")
	self.horizontalLayout.addWidget(self.pushButton_ok)
	self.verticalLayout_2.addLayout(self.horizontalLayout)
	self.verticalLayout.addWidget(self.frame_bottom)
	self.pushButton_ok.setObjectName("hight_button")


class modify_filename(QDialog, Ui_modify_filename):
    m_path=""
    m_rule_list=[]
    m_sou_file_list=[]
    m_des_file_list=[]

    COL_DES_NAME=0

    #边框参数
    m_enum_data=None #枚举数据
    m_direction=None
    m_is_left_press_down=False
    m_drag_position=QPoint()

    def __init__(self, a_path, a_rule_list, a_sou_file_list, parent=None):
	super(modify_filename,self).__init__(parent)
	self.setupUi(self)
	self.__translate__()

	self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
	self.setMouseTracking(True)  #添加鼠标追踪

	self.m_enum_data=self.__enum(UP=0, DOWN=1, LEFT=2, RIGHT=3, LEFTTOP=4, LEFTBOTTOM=5, RIGHTBOTTOM=6, RIGHTTOP=7, NONE=8)
	self.m_direction=self.m_enum_data.NONE
	self.frame_top.enterEvent=self.frame_enterEvent#子控件的事件要加上。自己界面的不需要
	self.frame_bottom.enterEvent=self.frame_enterEvent#子控件的事件要加上。自己界面的不需要

	self.pushButton_close.clicked.connect(self.slt_close)
	self.pushButton_ok.clicked.connect(self.slt_ok)
	self.connect(self.checkBox, SIGNAL('clicked(bool)'), self.slt_checkbox_clicked)

	self.m_path=a_path
	self.m_rule_list=a_rule_list
	self.m_sou_file_list=a_sou_file_list
	self.label_title.setText(self.tr("Please rename the file"))
	self.init_info()

	self.set_style()
	
    def run(self):
	self.exec_()
	return self.m_des_file_list
	
    def __translate__(self):
	self.checkBox.setText(self.tr("Add version (Only replace '#')"))
	self.pushButton_ok.setText(self.tr("OK"))


    def init_info(self):
	#显示规则
	self.label.setText(self.tr("File Rule('#':number '?':letter '*':Any character)")+"\n")

	pixmap=QPixmap(15,15)
	t_current_row=-1
	self.tableWidget.clear()
	self.set_header()
	self.tableWidget.setRowCount(0)
	is_all_char=False
	is_match_suffix=False
	if unicode("*") in self.m_rule_list:
	    #表示里面有*,规则就不默认为第一个
	    is_all_char=True

	for temp_sou_file in self.m_sou_file_list:
	    t_current_row=self.tableWidget.rowCount()
	    self.tableWidget.insertRow(t_current_row)
	    info=QFileInfo(temp_sou_file)
	    item=QTableWidgetItem()
	    if not ct_lib.com().is_match_regexp_list(self.m_rule_list, info.fileName()):
		pixmap.fill(Qt.red)
	    else:
		pixmap.fill(QColor(56,56,56))

	    item.setData(Qt.DescendingOrder, pixmap)
	    item.setData(Qt.UserRole, temp_sou_file)
	    self.tableWidget.setItem(t_current_row, self.COL_DES_NAME, item)

	    com=QComboBox(self.tableWidget)
	    #将源路径也藏一个到combobox的windowtitle中,用于后面替换suffix使用
	    com.setWindowTitle(temp_sou_file)
	    
	    com.currentIndexChanged.connect(self.slt_combobox_change)   
	    com.setView(QListView(self))
	    com.setEditable(True)
	    com.addItems(self.m_rule_list)
	    com.setCurrentText(info.fileName())
	    if len(self.m_rule_list)>0 and  not is_all_char:
		#匹配后缀名是一样的
		is_match_suffix=False
		for temp_rule in self.m_rule_list:
		    rule_info=QFileInfo(temp_rule)
		    if unicode(rule_info.suffix()).lower()==unicode(info.suffix()).lower():
			com.setCurrentText(temp_rule)
			is_match_suffix=True
			break

		if not is_match_suffix:
		    com.setCurrentText(self.replace_suffix(temp_sou_file, self.m_rule_list[0]))
			

	    self.tableWidget.setCellWidget(t_current_row, self.COL_DES_NAME, com)    

    #命名规则的后缀为*,默认直接填写上源文件的后缀
    def replace_suffix(self, a_sou_file, a_rule_string):
	rule_info=QFileInfo(a_rule_string)
	if unicode(rule_info.suffix())=="*":
	    info=QFileInfo(a_sou_file)	    
	    return rule_info.completeBaseName()+"."+info.suffix()
	else:
	    return a_rule_string

    def set_header(self):
	self.tableWidget.setColumnCount(0)
	headers=["File Name"]
	self.tableWidget.setColumnCount(len(headers))
	self.tableWidget.setHorizontalHeaderLabels(headers)
	self.tableWidget.horizontalHeader().setVisible(False)
	self.tableWidget.horizontalHeader().setStretchLastSection(True)
	self.tableWidget.verticalHeader().setVisible(False)
	self.tableWidget.setEditTriggers ( QAbstractItemView.NoEditTriggers )
	self.tableWidget.setShowGrid(False)
	self.tableWidget.setSortingEnabled(False)
	self.tableWidget.horizontalHeader().setDefaultAlignment (Qt.AlignLeft | Qt.AlignVCenter)
	self.tableWidget.setFocusPolicy(Qt.NoFocus)#取消高亮


    def is_exist_error(self):
	is_error=False
	user_data=""
	pixmap=QPixmap(15,15)
	rule_error=""
	filename_extension_error=""
	for i in range(self.tableWidget.rowCount()):
	    comboBox=self.tableWidget.cellWidget(i, self.COL_DES_NAME)
	    user_data=self.tableWidget.item(i, self.COL_DES_NAME).data(Qt.UserRole)

	    if not comboBox is None:
		text=comboBox.currentText()
		if not ct_lib.com().is_match_regexp_list(self.m_rule_list, text):
		    pixmap.fill(Qt.red)
		    is_error=True
		    rule_error=rule_error+text+"\n"
		else:
		    pixmap.fill(QColor(56,56,56))

		#检查后缀
		sou_info=QFileInfo(user_data)
		des_info=QFileInfo(text)
		if sou_info.suffix()!=des_info.suffix():
		    filename_extension_error=filename_extension_error+text+" <--> "+sou_info.fileName()+"\n";
		    is_error=True;
		    pixmap.fill(Qt.red)
		else:
		    pixmap.fill(QColor(56,56,56))

		self.tableWidget.item(i, self.COL_DES_NAME).setData(Qt.DescendingOrder, pixmap)

	if is_error:
	    error=""
	    if unicode(rule_error).strip()!="":
		error=self.tr("File rule error:")+"\n"+rule_error

	    if unicode(filename_extension_error).strip()!="":
		if error!="":
		    error=error+"\n"+self.tr("Filename extension error:")+"\n"+filename_extension_error
		else:
		    error=self.tr("Filename extension error:")+"\n"+filename_extension_error

	    ct_ui.message().error(error)
	return is_error



    #以下是自动版本--
    def get_index_dict(self, a_rule):
	s_id=-1
	e_id=-1
	#从后面往前找#
	e_id=unicode(a_rule).rfind("#")
	if e_id==-1:
	    return {"s_id":s_id, "e_id":e_id}

	temp=a_rule[0:e_id]
	for i in range(len(temp)):
	    if temp[len(temp)-i-1: len(temp)-i]!="#":
		s_id=len(temp)-i
		break
	if s_id==-1:
	    s_id=e_id

	return {"s_id":s_id, "e_id":e_id}

    def get_char(self, a_size):
	temp=""
	for i in range(a_size):
	    temp=temp+"#"
	return temp

    def check_version_exist(self, a_rule):
	t_dir=QDir(self.m_path)
	t_dir.setNameFilters(ct_lib.com().change_to_file_rule_list([rule]))
	t_dir.setFilter(QDir.Files | QDir.NoDotAndDotDot)
	for fileInfo in  t_dir.entryInfoList():
	    if ct_lib.com().is_match_regexp_string(rule, fileInfo.fileName()):
		return True
	return False

    def get_match_version_list(self, a_rule):
	filename_list=[]
	t_dir=QDir(self.m_path)
	t_dir.setNameFilters(ct_lib.com().change_to_file_rule_list([a_rule]))
	t_dir.setFilter(QDir.Files | QDir.NoDotAndDotDot)
	for fileInfo in  t_dir.entryInfoList():
	    if ct_lib.com().is_match_regexp_string(a_rule, fileInfo.fileName()):
		filename_list.append(fileInfo.fileName())
	return filename_list

    def set_combobox_data(self, a_combobox_widget):
	ver=-1
	rule=a_combobox_widget.currentText()
	t_dic=self.get_index_dict(rule)
	s_id=t_dic["s_id"]
	e_id=t_dic["e_id"]
	if e_id!=-1:
	    ver_size=e_id-s_id+1; #  "#"的个数
	    char_string=self.get_char(ver_size); #"####"
	    replace_b=rule[s_id: ] #比如"####.ma"
	    match_filename_list=self.get_match_version_list(rule)
	    match_filename_list.sort()
	    if len(match_filename_list)==0:
		ver=1
	    else:
		#取匹配到的最大的文件名的版本号
		max_ver=unicode(match_filename_list[len(match_filename_list)-1])[s_id: s_id+ver_size]
		ver=int(max_ver)+1

	    temp_rule=rule #重新赋值
	    temp_b=replace_b #重新赋值
	    replace_f=temp_b.replace(char_string, ct_lib.com().start_add_zero(unicode(ver),ver_size )) #比如"0001.ma"
	    new_rule=temp_rule.replace(replace_b, replace_f)
	    
	    #从combobox的windowtitle中取到这个源文件路径,用于后面替换suffix使用
	    temp_sou_file=a_combobox_widget.windowTitle()
	    a_combobox_widget.setCurrentText( self.replace_suffix(temp_sou_file, new_rule) )



    def __enum(self, **enums):
	return type('Enum', (), enums)

    def region(self, cursorGlobalPoint):
	frameWidth=5 #边框宽度
	rect = self.rect()
	tl = self.mapToGlobal(rect.topLeft())
	rb = self.mapToGlobal(rect.bottomRight())

	if QRect(tl.x(), tl.y(), frameWidth, frameWidth).contains(cursorGlobalPoint):
	    # 左上角
	    self.m_direction=self.m_enum_data.LEFTTOP
	    self.setCursor(QCursor(Qt.SizeFDiagCursor))

	elif QRect(rb.x()-frameWidth, rb.y()-frameWidth, frameWidth, frameWidth).contains(cursorGlobalPoint):
	    # 右下角
	    self.m_direction=self.m_enum_data.RIGHTBOTTOM
	    self.setCursor(QCursor(Qt.SizeFDiagCursor))

	elif QRect(tl.x(), rb.y()-frameWidth, frameWidth, frameWidth).contains(cursorGlobalPoint):
	    #左下角
	    self.m_direction=self.m_enum_data.LEFTBOTTOM
	    self.setCursor(QCursor(Qt.SizeBDiagCursor))

	elif QRect(rb.x()-frameWidth, tl.y(), frameWidth, frameWidth).contains(cursorGlobalPoint):
	    # 右上角
	    self.m_direction=self.m_enum_data.RIGHTTOP
	    self.setCursor(QCursor(Qt.SizeBDiagCursor))

	elif QRect(tl.x(), tl.y()+frameWidth, frameWidth, rect.height()-frameWidth*2).contains(cursorGlobalPoint):
	    # 左边
	    self.m_direction=self.m_enum_data.LEFT
	    self.setCursor(QCursor(Qt.SizeHorCursor))

	elif QRect(rb.x()-frameWidth, tl.y()+frameWidth, frameWidth, rect.height()-frameWidth*2).contains(cursorGlobalPoint):
	    # 右边
	    self.m_direction=self.m_enum_data.RIGHT
	    self.setCursor(QCursor(Qt.SizeHorCursor))

	elif QRect(tl.x()+frameWidth, tl.y(), rect.width()-frameWidth*2, frameWidth).contains(cursorGlobalPoint):
	    # 上边
	    self.m_direction=self.m_enum_data.UP
	    self.setCursor(QCursor(Qt.SizeVerCursor))

	elif QRect(rb.x()-rect.width()+frameWidth, rb.y()-frameWidth, rect.width()-frameWidth*2, frameWidth).contains(cursorGlobalPoint):
	    # 下边
	    self.m_direction=self.m_enum_data.DOWN
	    self.setCursor(QCursor(Qt.SizeVerCursor))

	else:
	    # 默认
	    self.m_direction=self.m_enum_data.NONE
	    self.setCursor(QCursor(Qt.ArrowCursor))

    #style---------------------
    def set_style(self):
	self.label_title.setStyleSheet("font-size:14px")
	self.pushButton_close.setStyleSheet("border:0px")

    #slot------------------------
    def slt_combobox_change(self, a_string):
	comboBox=self.sender()
	if not comboBox is None:	
	    if self.checkBox.isChecked()==True:
		self.set_combobox_data(comboBox)
	    else:
		#从combobox的windowtitle中取到这个源文件路径,用于后面替换suffix使用
		temp_sou_file=comboBox.windowTitle()
		comboBox.setCurrentText( self.replace_suffix(temp_sou_file, comboBox.currentText()) )		
			    

	    

    def slt_ok(self):
	try:
	    self.m_des_file_list=[]
	    if self.is_exist_error():
		return

	    for i in range(self.tableWidget.rowCount()):
		comboBox=self.tableWidget.cellWidget(i, self.COL_DES_NAME)
		self.m_des_file_list.append(self.m_path+"/"+comboBox.currentText())

	    self.accept()
	    self.close()

	except Exception, e:
	    ct_ui.message().error(e.message)

    def slt_checkbox_clicked(self, a_checked):
	if a_checked:
	    for i in range(self.tableWidget.rowCount()):
		combobox=self.tableWidget.cellWidget(i, self.COL_DES_NAME)
		if not combobox is None:
		    self.set_combobox_data(combobox)


    def slt_close(self):
	self.close()    


    #--------event--------------
    def frame_enterEvent(self, event):
	#默认
	self.m_direction=self.m_enum_data.NONE
	self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseReleaseEvent(self, event):
	if event.button() == Qt.LeftButton:
	    self.m_is_left_press_down = False
	    if self.m_direction != self.m_enum_data.NONE:
		self.releaseMouse()
		self.setCursor(QCursor(Qt.ArrowCursor))


    def mousePressEvent(self, event):
	if event.button()==Qt.LeftButton:
	    self.m_is_left_press_down=True
	    if self.m_direction != self.m_enum_data.NONE:
		self.mouseGrabber()
	    else:
		self.m_drag_position = event.globalPos() - self.frameGeometry().topLeft()    

    def mouseMoveEvent(self, event):
	gloPoint = event.globalPos()
	rect = self.rect()
	tl = self.mapToGlobal(rect.topLeft())
	rb = self.mapToGlobal(rect.bottomRight())

	if not self.m_is_left_press_down:
	    self.region(gloPoint)  
	else:
	    if self.m_direction != self.m_enum_data.NONE :
		rmove=QRect(tl, rb)
		if self.m_direction==self.m_enum_data.LEFT:
		    if rb.x() - gloPoint.x() <= self.minimumWidth():
			rmove.setX(tl.x())
		    else:
			rmove.setX(gloPoint.x())
		elif self.m_direction==self.m_enum_data.RIGHT :
		    rmove.setWidth(gloPoint.x() - tl.x())

		elif self.m_direction==self.m_enum_data.UP :
		    if rb.y() - gloPoint.y() <= self.minimumHeight() :
			rmove.setY(tl.y())
		    else:
			rmove.setY(gloPoint.y())

		elif self.m_direction==self.m_enum_data.DOWN :
		    rmove.setHeight(gloPoint.y() - tl.y())

		elif self.m_direction==self.m_enum_data.LEFTTOP :
		    if rb.x() - gloPoint.x() <= self.minimumWidth():
			rmove.setX(tl.x())
		    else:
			rmove.setX(gloPoint.x())
		    if rb.y() - gloPoint.y() <= self.minimumHeight():
			rmove.setY(tl.y())
		    else:
			rmove.setY(gloPoint.y())

		elif self.m_direction==self.m_enum_data.RIGHTTOP :
		    rmove.setWidth(gloPoint.x() - tl.x())
		    rmove.setY(gloPoint.y())

		elif self.m_direction==self.m_enum_data.LEFTBOTTOM:
		    rmove.setX(gloPoint.x())
		    rmove.setHeight(gloPoint.y() - tl.y())

		elif self.m_direction==self.m_enum_data.RIGHTBOTTOM:
		    rmove.setWidth(gloPoint.x() - tl.x())
		    rmove.setHeight(gloPoint.y() - tl.y())

		else:
		    pass
		self.setGeometry(rmove)
	    else:
		self.move(event.globalPos() - self.m_drag_position)
		event.accept()


    def paintEvent(self, e):
	pen=QPen()
	painter=QPainter(self)
	pen.setColor(QColor("#E5E6E7"))
	painter.setPen(pen)
	painter.drawRect(0, 0, self.width()-1, self.height()-1)

    def keyPressEvent(self, event):
	#防止按esc退出
	if event.key()==Qt.Key_Escape:
	    pass
	
	
  



#ct_base类名是固定的
class ct_base(ct_plu.extend):
    def __init__(self):
	ct_plu.extend.__init__(self)#继承

    #取文件框规则
    def get_filebox_info(self, a_tw, a_db, a_module, a_module_type, a_task_id, a_filebox_id):
	t_os=a_tw.sys().get_sys_os()
	dic={"db":a_db, "module":a_module, "module_type":a_module_type, "task_id": a_task_id, "filebox_id":a_filebox_id, "os":t_os}
	res=a_tw.con()._send("c_file","filebox_get_one_with_id", dic)
	if isinstance(res, dict):
	    return res
	return False
     

    #重写run,外部调用
    def run(self, a_dict_data):
	t_argv=ct_plu.argv(a_dict_data)
	t_db=t_argv.get_sys_database()
	t_module=t_argv.get_sys_module()
	t_module_type=t_argv.get_sys_module_type()
	t_id_list=t_argv.get_sys_id()
	t_filebox_id=t_argv.get_sys_filebox_id()
	t_drop_file_list=t_argv.get_sys_file()#拖入进来的源文件
	try:
	    t_tw = tw()
	    #取命名规则和路径
	    filebox_info=self.get_filebox_info(t_tw, t_db, t_module, t_module_type, t_id_list[0], t_filebox_id)
	    if filebox_info==False or not filebox_info.has_key("rule") or not filebox_info.has_key("path"):
		return self.ct_false("Get filebox info error")
	    t_rule_list=filebox_info["rule"]
	    t_path=filebox_info["path"]
	    if not isinstance(t_rule_list, list):
		return self.ct_false("Get filebox rule error")	    
	    
	    #取出目录规则,用于提示
	    message_folder_rule=""
	    for temp_rule in t_rule_list:
		if unicode(temp_rule).find(".")==-1:
		    message_folder_rule=message_folder_rule+"\n"+temp_rule	   
	    
	    #-----------------------------组成新的-----------------------
	    sou_file_list=[]
	    des_file_list=[]
	    sou_dir_list=[]
	    des_dir_list=[]
	    total_sou_list=[]
	    total_des_list=[]	    
	    is_exist_error_filename=False
	    #过滤出符合命名规则的文件 //文件是否存在命名规则错误
	    for temp_path in t_drop_file_list:
		t_filename=os.path.basename(temp_path)
		if os.path.isfile(temp_path):
		    if not ct_lib.com().is_match_regexp_list(t_rule_list, t_filename):
			is_exist_error_filename=True
		    sou_file_list.append(temp_path)
		    des_file_list.append(t_path+"/"+t_filename)
		else:
		    #检查文件夹
		    if not ct_lib.com().is_match_regexp_list(t_rule_list, t_filename):
			#目录规则错误
			return self.ct_false("Folder rule is error \n"+message_folder_rule)
	
		    sou_dir_list.append(temp_path)
		    #不是遍历的，里面存储的就是文件夹的路径。。
		    des_dir_list.append(t_path+"/"+t_filename)	
	    
	    #存在命名规则错误,进行更改
	    if is_exist_error_filename:
		#修改文件名,并返回目标文件列表
		res=modify_filename(t_path, t_rule_list, sou_file_list).run()
		if res==[]:
		    return self.ct_false("Fail to modify the rules")#修改规则失败
		des_file_list=res	    

	    #把文件和文件夹的都放到新的列表中----
	    total_sou_list=total_sou_list+sou_file_list
	    total_sou_list=total_sou_list+sou_dir_list
	    total_des_list=total_des_list+des_file_list
	    total_des_list=total_des_list+des_dir_list
	    return self.ct_true({"sou_list":total_sou_list, "des_list":total_des_list})
	except Exception,e:
	    #print traceback.format_exc()
	    return self.ct_false(traceback.format_exc())

if __name__ == "__main__":
    #调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict=ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)
