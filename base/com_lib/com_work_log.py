# -*- coding: utf-8 -*-
#Author:王晨飞
#Time  :2017-12-19
#Describe:改为多线程,这样才是真正的实施打印工作日志
#         QPushButton新增
#         CgTeamWork V5整合
import os
import sys
import Queue
import threading
from com_widget      import *
from com_message_box import *
class plugin_log_signal(QObject):
    t_signal = Signal(str,str,bool)
class plugin_log_widget(widget):
    def __init__(self):
        super(plugin_log_widget,self).__init__()
        self.set_UI()
        self.set_Style()
    def set_UI(self):
        self.__ui__()
        self.setMinimumSize(600,400)
        self.m_title_label.setText(u"插件工作日志")
        self.m_input_text = QTextEdit()
        self.m_input_text.setReadOnly(True)
        self.parent_lay.addWidget(self.m_input_text)
    def set_Style(self):
        self.m_input_text.setStyleSheet("QTextEdit{border-radius:4px;border:1px solid #E5E6E7;font-size:12px;color:#666666;}")
    def slt_show_error(self, a_data, a_is_close=True):
        message().error(a_data,a_is_close)
    def slt_show_info(self, a_data, a_is_close=True):
        message().info(a_data,a_is_close)
    def slt_show_question(self, a_data):
        t_dict = {}
        message().question(a_data,t_dict)
        if t_dict["is_ok"]=="Y":
            self.m_queue.put("Y")
        else:
            self.m_queue.put("N")
    def slt_add_log(self, a_text):
        try:
            self.m_input_text.insertPlainText( a_text + "\n" )
            cursor =  self.m_input_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.m_input_text.setTextCursor(cursor)
        except:
            return False
    def slt_signal(self, a_type, a_message, a_is_exit=True):
        if a_type=="info":
            self.slt_show_info(a_message,a_is_exit)
        elif a_type=="error":
            self.slt_show_error(a_message,a_is_exit)  
        elif a_type=="question":
            self.slt_show_question(a_message)
        elif a_type=="log":
            self.slt_add_log(a_message)
        elif a_type=="QFileDialog":
            t_des_path = QFileDialog.getExistingDirectory(None,a_message).replace("\\", "/")
            self.m_queue.put(t_des_path)
        elif a_type == "QPushButton":
            self.slt_button_start()
        else:
            sys.exit()
        self.m_event.set()
        self.m_event.clear()
    def slt_button_stop(self):
        if self.m_button!=False:
            try:
                self.m_button.setEnabled(False)
            except Exception,e:
                pass
    def slt_button_start(self):
        if self.m_button!=False:
            try:
                self.m_button.setEnabled(True)
            except Exception,e:
                pass
    def run(self, a_function, a_data, a_button=False):
        self.m_button = a_button
        self.m_queue  = Queue.Queue()
        self.m_event  = threading.Event()
        self.slt_button_stop()
        self.m_signal = plugin_log_signal()
        self.m_signal.t_signal.connect(self.slt_signal)
        self.m_thread = threading.Thread(target=a_function, args=(a_data, self.m_queue, self.m_signal.t_signal, self.m_event))
        self.m_thread.setDaemon(True)
        self.m_thread.start()
def show_log(a_function, a_data, a_is_show):
    app = QApplication(sys.argv)
    win = plugin_log_widget()
    win.run(a_function, a_data)
    if a_is_show:
        win.show()
    app.exec_()