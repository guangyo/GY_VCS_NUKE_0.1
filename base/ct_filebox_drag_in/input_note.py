#coding:utf-8
"""
  Author:  shiming
  Purpose: 输入Note
  Created: 2018-03-13
"""
import os
import sys
import traceback
import json

#加载ct_plu库
t_base_path=unicode(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/")
if t_base_path not in sys.path:
    sys.path.append(t_base_path)
try:
    from cgtw import *
    import ct_plu
    from ct_plu.qt import *#导入QT的库
except Exception,e:
    print traceback.format_exc()    

class Ui_filebox_drag_in_input_note(object):
    def setupUi(self, filebox_drag_in_input_note):
        filebox_drag_in_input_note.setObjectName("filebox_drag_in_input_note")
        filebox_drag_in_input_note.resize(489, 337)
        self.verticalLayout = QVBoxLayout(filebox_drag_in_input_note)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_top = QFrame(filebox_drag_in_input_note)
        self.frame_top.setMinimumSize(QSize(0, 40))
        self.frame_top.setMaximumSize(QSize(16777215, 40))
        self.frame_top.setFrameShape(QFrame.StyledPanel)
        self.frame_top.setFrameShadow(QFrame.Raised)
        self.frame_top.setObjectName("frame_top")
        self.horizontalLayout_2 = QHBoxLayout(self.frame_top)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(17, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_title = QLabel(self.frame_top)
        self.label_title.setMinimumSize(QSize(0, 21))
        self.label_title.setText("")
        self.label_title.setScaledContents(True)
        self.label_title.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_title.setWordWrap(True)
        self.label_title.setObjectName("label_title")
        self.horizontalLayout_2.addWidget(self.label_title)
        self.pushButton_close = QPushButton(self.frame_top)
        self.pushButton_close.setMinimumSize(QSize(25, 25))
        self.pushButton_close.setMaximumSize(QSize(25, 25))
        self.pushButton_close.setText("")
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/close.png"), QIcon.Normal, QIcon.Off)
        self.pushButton_close.setIcon(icon)
        self.pushButton_close.setFlat(True)
        self.pushButton_close.setObjectName("pushButton_close")
        self.horizontalLayout_2.addWidget(self.pushButton_close)
        self.verticalLayout.addWidget(self.frame_top)
        self.frame_view = QFrame(filebox_drag_in_input_note)
        self.frame_view.setFrameShape(QFrame.StyledPanel)
        self.frame_view.setFrameShadow(QFrame.Raised)
        self.frame_view.setObjectName("frame_view")
        self.verticalLayout_2 = QVBoxLayout(self.frame_view)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.textEdit = QTextEdit(self.frame_view)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_2.addWidget(self.textEdit)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_ok = QPushButton(self.frame_view)
        self.pushButton_ok.setMinimumSize(QSize(60, 28))
        self.pushButton_ok.setMaximumSize(QSize(60, 28))
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.horizontalLayout.addWidget(self.pushButton_ok)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.frame_view)

#Note编辑窗口
class filebox_drag_in_input_note(QDialog, Ui_filebox_drag_in_input_note):

    #边框参数
    m_enum_data=None #枚举数据
    m_direction=None
    m_is_left_press_down=False
    m_drag_position=QPoint()
    
    m_res=False
    def __init__(self, parent=None):
        super(filebox_drag_in_input_note,self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setMouseTracking(True)  #添加鼠标追踪
        
        self.m_enum_data=self.__enum(UP=0, DOWN=1, LEFT=2, RIGHT=3, LEFTTOP=4, LEFTBOTTOM=5, RIGHTBOTTOM=6, RIGHTTOP=7, NONE=8)
        self.m_direction=self.m_enum_data.NONE
        self.frame_top.enterEvent=self.frame_enterEvent#子控件的事件要加上。自己界面的不需要
        self.frame_view.enterEvent=self.frame_enterEvent#子控件的事件要加上。自己界面的不需要
        
        self.pushButton_close.clicked.connect(self.slt_close)
        self.pushButton_ok.clicked.connect(self.slt_ok)
        self.pushButton_ok.setText(self.tr("OK"))
        self.label_title.setText("Input Note")
        self.set_style()
    
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
            
    
    def run(self):
        self.exec_()
        return self.m_res
    
    #style---------------------
    def set_style(self):
        self.label_title.setStyleSheet("font-size:14px;")
        self.pushButton_close.setStyleSheet("border:0px")
        
        
    #slot------------------------
    def slt_close(self):
        self.close()
    
    def slt_ok(self):
        self.m_res=self.textEdit.toPlainText()
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
        up_background=""
        up_border=""
        down_backgroud=""
        down_border=""
        
        theme="default"
        if theme=="maya":
            up_background="#373737"
            up_border="#555555"
            down_backgroud="#373737"
            down_border="#555555"            
        elif theme=="black":
            up_background="#323b44"
            up_border="#434F5C"
            down_backgroud="#323b44"
            down_border="#434F5C"
        else:
            up_background="#fafafa"
            up_border="#E5E6E7"
            down_backgroud="#F5F5F5"
            down_border="#E5E6E7"            
        
        #画上面背景色
        painter.setBrush(QColor(up_background))
        pen.setColor(QColor(up_border))
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width()-1, 40)
    
    
        #画下面
        painter.setBrush(QColor(down_backgroud))
        pen.setColor(QColor(down_border));#画边线
        painter.setPen(pen)
        painter.drawRect(0, 40, self.width()-1, self.height()-41)       
   
    def keyPressEvent(self, event):
        #防止按esc退出
        if event.key()==Qt.Key_Escape:
            pass
        
        
#ct_base类名是固定的
class ct_base(ct_plu.extend):
    def __init__(self):
        ct_plu.extend.__init__(self)#继承
    
    #重写run,外部调用
    def run(self, a_dict_data):
        try:
            t_res=filebox_drag_in_input_note().run()
            #最后要返回
            if t_res==False:
                return self.ct_false("No input note")
            else:
                return self.ct_true(t_res)
            
        except Exception,e:
            #print traceback.format_exc()
            return self.ct_false(traceback.format_exc())
        
if __name__ == "__main__":
    app=QApplication(sys.argv)
    #调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict=ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)
    app.exec_()      
        
