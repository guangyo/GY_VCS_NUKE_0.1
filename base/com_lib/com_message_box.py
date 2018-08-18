# -*- coding: utf-8 -*-
#Author:王晨飞 
#Time  :2017-12-19
#Describe:从新整理,兼顾子进程
#         CgTeamWork V5整合
import os
import sys
m_pyside = os.path.dirname(os.path.dirname(os.path.dirname(__file__.replace("\\","/"))))+"/lib/pyside"
if not m_pyside in sys.path:
    sys.path.append(m_pyside)
from PySide2.QtCore    import *
from PySide2.QtGui     import *
from PySide2.QtWidgets import *
QApplication.addLibraryPath(m_pyside+"/PySide2/plugins/")
class message(QDialog):
    m_is_left       = False
    m_is_drag       = False
    m_icon_path     = os.path.dirname(os.path.dirname(__file__).replace("\\","/"))+"/com_icon/"
    m_return_dict   = {}
    m_is_exit       = False
    def __init__(self):
        try:
            if QApplication.instance() is None:
                self.my_new_app=QApplication([])
        except Exception,e:
            return 
        super(message,self).__init__()
    def __UI__(self):
        self.setMinimumSize(200,120)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        lay = QVBoxLayout()
        lay.setContentsMargins(8,0,0,0)
        self.setLayout(lay)
        self.m_frame = QFrame()
        lay.addWidget( self.m_frame )
        lay_frame = QVBoxLayout()
        self.m_frame.setLayout(lay_frame)

        self.m_icon_label = QLabel()
        self.m_icon_label.setFixedSize(32,32)
        self.m_text_label = QLabel()
        self.m_text_label.setText(self.m_text)


        lay_icon = QVBoxLayout()
        lay_icon.addStretch()
        lay_icon.addWidget(self.m_icon_label)
        lay_icon.addStretch()

        lay_label = QHBoxLayout()
        lay_label.addLayout( lay_icon )
        lay_label.addWidget( self.m_text_label )
        lay_label.setSpacing(24)
        lay_frame.addLayout( lay_label )

        lay_button = QHBoxLayout()
        lay_button.addStretch()
        if self.m_has_cancel:
            self.m_cancel_button = QPushButton()
            self.m_cancel_button.setText(u"取消")
            self.m_cancel_button.setFixedSize(60,28)
            self.m_cancel_button.clicked.connect(self.slt_cancel)
            lay_button.addWidget(self.m_cancel_button)                  
        if self.m_has_ok:
            self.m_ok_button = QPushButton()
            self.m_ok_button.setText(u"确定")
            self.m_ok_button.setFixedSize(60,28)
            self.m_ok_button.clicked.connect(self.slt_ok)
            lay_button.addWidget(self.m_ok_button)
        lay_frame.addLayout(lay_button)
        self.set_style()                
    def info(self, a_text, a_is_exit=True):
        self.m_icon       = self.m_icon_path + "info.png"
        self.m_text       = a_text
        self.m_is_exit     = a_is_exit
        self.m_has_ok     = True
        self.m_has_cancel = False
        self.__UI__()
        self.exec_()
    def error(self, a_text, a_is_exit=True):
        self.m_icon       = self.m_icon_path + "error.png"
        self.m_text       = a_text
        self.m_is_exit    = a_is_exit
        self.m_has_ok     = True
        self.m_has_cancel = False
        self.__UI__()
        self.exec_()
    def question(self, a_text, a_return_dict = {}):
        self.m_icon        = self.m_icon_path + "question.png"
        self.m_text        = a_text
        self.m_return_dict = a_return_dict
        self.m_has_ok      = True
        self.m_has_cancel  = True
        self.__UI__()
        self.exec_()
    #----------------------------------------slt--------------------------------------
    def slt_ok(self):
        self.m_return_dict["is_ok"] = "Y" 
        if self.m_is_exit:
            sys.exit()
        else:
            self.close()
    def slt_cancel(self):
        self.m_return_dict["is_ok"] = "N" 
        if self.m_is_exit:
            sys.exit()
        else:
            self.close()
    #----------------------------------------style------------------------------------
    def set_style(self):
        self.m_icon_label.setStyleSheet("QLabel{border-image:url(%s)}"%self.m_icon)
        self.m_text_label.setStyleSheet("QLabel{font-size:12px; color:#666666;}")
        if self.m_has_ok:
            self.m_ok_button.setStyleSheet("QPushButton{background-color:#108ee9;color:#FFFFFF;font-size:12px;border-radius:4px;}"
                                           "QPushButton:hover{background-color:#1083E0; border-radius:4px; font-size:12px; color:#FFFFFF;}"
                                           )
        if self.m_has_cancel:
            self.m_cancel_button.setStyleSheet("QPushButton{background-color:#FFFFFF;color:#666666;font-size:12px;border-radius:4px;border:1px solid #999999;}"
                                               "QPushButton:hover{background-color:#FFFFFF; border-radius:4px; font-size:12px; color:#0F87DE;border:1px solid #0F87DE}"
                                               )                        
    #----------------------------------------event------------------------------------
    def mousePressEvent(self, event):
        if event.button()==Qt.LeftButton:
            self.m_is_left = True
            self.m_is_drag   = True
            self.m_begin_pos = event.globalPos()-self.pos()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            event.accept()
    def mouseMoveEvent(self, event):
        if self.m_is_left :
            if self.m_is_drag :
                self.m_end_pos = event.globalPos()
                self.move(self.m_end_pos - self.m_begin_pos)
                event.accept()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_is_left = False
            if self.m_is_drag:
                self.m_is_drag = False
                self.setCursor(QCursor(Qt.ArrowCursor))
                event.accept() 
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.white)
        pen=QPen()
        pen.setColor(QColor("#999999"))
        painter.setPen(pen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 5,5)
