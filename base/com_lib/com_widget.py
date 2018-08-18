# -*- coding: utf-8 -*-
#Author:王晨飞 
#Time  :2017-12-19
#Describe:无界面窗口,自己写的缩放,移动,美化
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
class widget(QWidget):
    m_parent_padding       = 4
    m_parent_resize_status = 0
    m_parent_is_left       = False
    m_parent_is_drag       = False
    m_parent_is_resize     = False
    m_icon_path            = os.path.dirname(os.path.dirname(__file__).replace("\\","/"))
    def __ui__(self):
        self.setMinimumSize(600,500)
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.parent_lay = QVBoxLayout()
        self.setLayout(self.parent_lay)
        self.setContentsMargins(0,0,0,0)
        self.parent_lay.setContentsMargins(8,8,8,8)
        self.parent_lay.setSpacing(0)
        self.m_logo_button = QPushButton()
        self.m_logo_button.setFixedSize(24,24)
        self.m_title_label = QLabel()
        self.m_title_label.setText(u"CgTeamWork")
        self.m_minimize_button = QPushButton()
        self.m_minimize_button.setFixedSize(16,16)
        self.m_minimize_button.clicked.connect(self.showMinimized)
        self.m_close_button = QPushButton()
        self.m_close_button.setFixedSize(16,16)
        self.m_close_button.clicked.connect(self.close)
        lay_top_toolbar = QHBoxLayout()
        lay_top_toolbar.setContentsMargins(5,5,5,2)
        lay_top_toolbar.setSpacing(8)
        lay_top_toolbar.addWidget(self.m_logo_button)
        lay_top_toolbar.addWidget(self.m_title_label)
        lay_top_toolbar.addWidget(self.m_minimize_button)
        lay_top_toolbar.addWidget(self.m_close_button)
        self.parent_lay.addLayout(lay_top_toolbar)
        self.__style__()
    def __style__(self):
        self.setObjectName("main")
        self.setStyleSheet("#main{background-color:#F5F5F5;}"
                           "QScrollBar:vertical {background-color:#FFFFFF;border: 1px solid #FFFFFF;border-radius: 4px;width:10px;}"
                           "QScrollBar::handle:horizontal{background-color:#D6D6D6;border: 1px solid #D6D6D6;border-radius: 4px;min-width:25px;}"
                           "QScrollBar::handle:vertical{background-color:#D6D6D6;border: 1px solid #D6D6D6;border-radius: 4px;min-height:25px;}"
                           "QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical,QScrollBar::add-page:horizontal,QScrollBar::sub-page:horizontal{background-color:#FFFFFF;}"
                           "QScrollBar:horizontal {background-color:#FFFFFF;border: 1px solid #FFFFFF;border-radius: 4px;height:10px;}"
                           "QScrollBar::add-line:vertical ,QScrollBar::sub-line:vertical ,QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal {height:0px;width:0px;}"
                           )
        self.m_logo_button.setStyleSheet("QPushButton{border-image:url(" + self.m_icon_path + "/com_icon/logo.png)}")  
        self.m_title_label.setStyleSheet("QLabel{color:#666666;font-size:12px;}")
        self.m_minimize_button.setStyleSheet("QPushButton{border-image:url(" + self.m_icon_path + "/com_icon/min.png)}")  
        self.m_close_button.setStyleSheet("QPushButton{border-image:url(" + self.m_icon_path + "/com_icon/close.png)}") 
    def mousePressEvent(self, event):
        if event.button()==Qt.LeftButton:
            self.m_parent_is_left = True
            if self.m_parent_is_resize == False:
                self.m_parent_is_drag   = True
                self.m_begin_pos = event.globalPos()-self.pos()
                self.setCursor(QCursor(Qt.OpenHandCursor))
                event.accept()
    def mouseMoveEvent(self, event):
        if self.m_parent_is_left :
            if self.m_parent_is_drag :
                self.m_end_pos = event.globalPos()
                self.move(self.m_end_pos - self.m_begin_pos)
                event.accept()
            if self.m_parent_is_resize:
                self.m_mouse_pos   = event.globalPos()
                self.m_window_rect = self.rect()

                self.m_window_top_left     = self.mapToGlobal( self.m_window_rect.topLeft()     )
                self.m_window_bottom_right = self.mapToGlobal( self.m_window_rect.bottomRight() )
                self.m_mouse_x             = self.m_mouse_pos.x()
                self.m_mouse_y             = self.m_mouse_pos.y()

                t_move_rext = QRect( self.m_window_top_left, self.m_window_bottom_right )
                if self.m_parent_resize_status == 1 :
                    if self.m_window_bottom_right.x() - self.m_mouse_pos.x() <= self.minimumWidth():
                        t_move_rext.setX(self.m_window_top_left.x())
                    else:
                        t_move_rext.setX(self.m_mouse_pos.x())
                    if self.m_window_bottom_right.y() - self.m_mouse_pos.y() <= self.minimumHeight():
                        t_move_rext.setY(self.m_window_top_left.y())
                    else:
                        t_move_rext.setY(self.m_mouse_pos.y())
                elif self.m_parent_resize_status == 2 :
                    if self.m_mouse_pos.x() - self.m_window_top_left.x() >= self.minimumWidth():
                        t_move_rext.setWidth( self.m_mouse_pos.x() - self.m_window_top_left.x() )
                    if self.m_window_bottom_right.y() - self.m_mouse_pos.y() >= self.minimumHeight():
                        t_move_rext.setY( self.m_mouse_pos.y() )
                elif self.m_parent_resize_status == 3 :
                    if self.m_mouse_pos.x() - self.m_window_top_left.x() >= self.minimumWidth():
                        t_move_rext.setWidth( self.m_mouse_pos.x() - self.m_window_top_left.x() )
                    if self.m_mouse_pos.y() - self.m_window_top_left.y() >= self.minimumHeight():
                        t_move_rext.setHeight( self.m_mouse_pos.y() - self.m_window_top_left.y() )
                elif self.m_parent_resize_status == 4 :
                    if self.m_window_bottom_right.x() - self.m_mouse_pos.x() >= self.minimumWidth():
                        t_move_rext.setX( self.m_mouse_pos.x() )
                    if self.m_mouse_pos.y() - self.m_window_top_left.y() >= self.minimumHeight():
                        t_move_rext.setHeight( self.m_mouse_pos.y() -  self.m_window_top_left.y() )
                elif self.m_parent_resize_status == 5 :
                    if self.m_window_bottom_right.x() - self.m_mouse_pos.x() <= self.minimumWidth():
                        t_move_rext.setX( self.m_window_top_left.x() )
                    else:
                        t_move_rext.setX( self.m_mouse_pos.x() )
                elif self.m_parent_resize_status == 6 :
                    t_move_rext.setWidth( self.m_mouse_pos.x() - self.m_window_top_left.x() )
                elif self.m_parent_resize_status == 7 :
                    if self.m_window_bottom_right.y() - self.m_mouse_pos.y() <= self.minimumHeight():
                        t_move_rext.setY( self.m_window_top_left.y() )
                    else:
                        t_move_rext.setY( self.m_mouse_pos.y() )
                elif self.m_parent_resize_status == 8 :
                    t_move_rext.setHeight( self.m_mouse_pos.y() - self.m_window_top_left.y())
                self.setGeometry(t_move_rext)

        else:
            self.m_mouse_pos   = event.globalPos()
            self.m_window_rect = self.rect()

            self.m_window_top_left     = self.mapToGlobal( self.m_window_rect.topLeft()     )
            self.m_window_bottom_right = self.mapToGlobal( self.m_window_rect.bottomRight() )
            self.m_mouse_x             = self.m_mouse_pos.x()
            self.m_mouse_y             = self.m_mouse_pos.y()


            if self.m_window_top_left.x()+self.m_parent_padding >= self.m_mouse_x >= self.m_window_top_left.x()           and self.m_window_top_left.y()+self.m_parent_padding >= self.m_mouse_y >= self.m_window_top_left.y():
                self.setCursor(QCursor(Qt.SizeFDiagCursor))
                self.m_parent_is_resize = True
                self.m_parent_resize_status = 1
            elif self.m_window_bottom_right.x()-self.m_parent_padding <= self.m_mouse_x <= self.m_window_bottom_right.x() and self.m_window_top_left.y()+self.m_parent_padding >= self.m_mouse_y >= self.m_window_top_left.y():
                self.setCursor(QCursor(Qt.SizeBDiagCursor))
                self.m_parent_is_resize = True
                self.m_parent_resize_status = 2
            elif self.m_window_bottom_right.x()-self.m_parent_padding <= self.m_mouse_x <= self.m_window_bottom_right.x() and self.m_window_bottom_right.y()-self.m_parent_padding <= self.m_mouse_y <= self.m_window_bottom_right.y():
                self.setCursor(QCursor(Qt.SizeFDiagCursor))
                self.m_parent_is_resize = True
                self.m_parent_resize_status = 3
            elif self.m_window_top_left.x()+self.m_parent_padding >= self.m_mouse_x >= self.m_window_top_left.x()         and self.m_window_bottom_right.y()-self.m_parent_padding <= self.m_mouse_y <= self.m_window_bottom_right.y():
                self.setCursor(QCursor(Qt.SizeBDiagCursor))
                self.m_parent_is_resize = True
                self.m_parent_resize_status = 4
            elif self.m_window_top_left.y()+self.m_parent_padding < self.m_mouse_y < self.m_window_bottom_right.y()-self.m_parent_padding and self.m_window_top_left.x()+self.m_parent_padding > self.m_mouse_x > self.m_window_top_left.x():
                self.setCursor(QCursor(Qt.SizeHorCursor))
                self.m_parent_is_resize = True
                self.m_parent_resize_status = 5
            elif self.m_window_top_left.y()+self.m_parent_padding < self.m_mouse_y < self.m_window_bottom_right.y()-self.m_parent_padding and self.m_window_bottom_right.x()-self.m_parent_padding < self.m_mouse_x < self.m_window_bottom_right.x():
                self.setCursor(QCursor(Qt.SizeHorCursor))
                self.m_parent_is_resize = True
                self.m_parent_resize_status = 6
            elif self.m_window_top_left.y() < self.m_mouse_y < self.m_window_top_left.y()+self.m_parent_padding                    and self.m_window_top_left.x()+self.m_parent_padding < self.m_mouse_x < self.m_window_bottom_right.x():
                self.setCursor(QCursor(Qt.SizeVerCursor))
                self.m_parent_is_resize = True
                self.m_parent_resize_status = 7
            elif self.m_window_bottom_right.y()-self.m_parent_padding < self.m_mouse_y < self.m_window_bottom_right.y()            and self.m_window_top_left.x()+self.m_parent_padding < self.m_mouse_x < self.m_window_bottom_right.x():
                self.setCursor(QCursor(Qt.SizeVerCursor))
                self.m_parent_is_resize = True
                self.m_parent_resize_status = 8
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
                self.m_parent_is_resize = False
                self.m_parent_resize_status = 0
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_parent_is_left = False
            if self.m_parent_is_drag:
                self.m_parent_is_drag = False
                self.setCursor(QCursor(Qt.ArrowCursor))
                event.accept() 
            if self.m_parent_is_resize:
                self.m_parent_is_resize = False
                self.setCursor(QCursor(Qt.ArrowCursor))
                event.accept() 
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#F5F5F5"))
        pen=QPen()
        pen.setColor(QColor("#999999"))
        painter.setPen(pen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 5,5)

