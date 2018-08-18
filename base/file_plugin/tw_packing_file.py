# -*- coding: utf-8 -*-
# Author  :翁建华
# Time    :2018-05-18
# Describe:拷贝动作放到子线程,
#         维持旧版本
#         info,task均可使用,去除History
#         CgTeamWork_V5整理
#         重写Sorted排序  2018-05-18
import os
import re
import sys
import time
import json
import shutil
import datetime

G_base_path = os.path.dirname(os.path.dirname(__file__.replace("\\", "/")))
G_com_path = G_base_path + "/com_lib/"
G_cgtw_path = os.path.dirname(G_base_path) + "/cgtw/"
if not G_base_path in sys.path:
    sys.path.append(G_base_path)
if not G_com_path in sys.path:
    sys.path.append(G_com_path)
if not G_cgtw_path in sys.path:
    sys.path.append(G_cgtw_path)
import ct
from com_work_log import *
from com_message_box import *
from com_function import *
from cgtw import *
from com_widget import *


class pack_file_widget(widget):
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
            self.k_log_show = self.m_tw.sys().get_argv_key("is_show_log")
            self.k_not_folder = self.m_tw.sys().get_argv_key("no_pack_folder")
            self.m_module = self.m_tw.sys().get_sys_module()
            self.m_module_type = self.m_tw.sys().get_sys_module_type()
            self.class_pipeline = self.m_tw.pipeline(self.m_database)
            self.m_filebox_class = self.m_tw.filebox(self.m_database)
            if type(self.m_id_list) != list or len(self.m_id_list) == 0:
                message().error(u"请选择需要复制的任务!")

            if self.m_module_type == "info":
                self.m_module_class = self.m_tw.info_module(self.m_database, self.m_module)
            else:
                self.m_module_class = self.m_tw.task_module(self.m_database, self.m_module, self.m_id_list)
                t_data_list = self.m_module_class.get([self.m_module + ".id"])
                self.m_id_list = []
                for t_data in t_data_list:
                    self.m_id_list.append(t_data[self.m_module + ".id"])
                self.m_id_list = list(set(self.m_id_list))
                self.m_module_class = self.m_tw.info_module(self.m_database, self.m_module)

            self.m_pipeline_class = self.m_tw.pipeline(self.m_database)
            self.m_pipeline_list = self.m_pipeline_class.get_with_module(self.m_module, ["name", "#id"])
            if type(self.m_pipeline_list) != list or len(self.m_pipeline_list) == 0:
                message().error(u"取制作阶段列表失败, 请确认是否有配置制作阶段!")
            for pipeline in self.m_pipeline_list:
                t_filebox_list = self.m_filebox_class.get_with_pipeline_id(pipeline["id"], self.m_module)
                if type(t_filebox_list) == list and len(t_filebox_list) > 0:
                    pipeline_item = QTreeWidgetItem(self.treeWidget_sou)
                    pipeline_item.setText(0, pipeline["name"])
                    for i in t_filebox_list:
                        item = QTreeWidgetItem(pipeline_item)
                        item.setCheckState(0, Qt.Unchecked)
                        item.setText(0, i["title"])
                        item.setData(0, 32, i["id"])
        except Exception, e:
            message().error(u"读取数据库失败")
        self.set_Style()
        self.show()
        self.m_work_log = plugin_log_widget()
        if str(self.k_log_show).lower() == "y":
            t_x = self.pos().x()
            t_y = self.pos().y()
            self.m_work_log.move(t_x + 350, t_y)
            self.m_work_log.setMinimumSize(300, 400)
            self.m_work_log.show()
            self.move(t_x - 150, t_y)

    def set_UI(self):
        self.setMinimumSize(500, 400)
        self.m_title_label.setText(u"打包文件到所选目录")
        self.treeWidget_sou = QTreeWidget()
        self.treeWidget_sou.setHeaderLabel(u"阶段/文件筐")
        self.parent_lay.addWidget(self.treeWidget_sou)
        self.m_all_check_file_checkbox = QCheckBox()
        self.m_all_check_file_checkbox.setText(u"目录下所有文件")
        self.m_save_folder_checkbox = QCheckBox()
        self.m_save_folder_checkbox.setText(u"保持目录结构")
        self.m_copy_button = QPushButton()
        self.m_copy_button.setText(u"确定")
        lay_bottom_toolbar = QHBoxLayout()
        lay_bottom_toolbar.addWidget(self.m_all_check_file_checkbox)
        lay_bottom_toolbar.addWidget(self.m_save_folder_checkbox)
        lay_bottom_toolbar.addStretch()
        lay_bottom_toolbar.addWidget(self.m_copy_button)
        lay_bottom_toolbar.setContentsMargins(0, 8, 0, 0)
        self.parent_lay.addLayout(lay_bottom_toolbar)
        self.m_copy_button.clicked.connect(self.slt_copy)
        self.m_close_button.clicked.connect(self.slt_close)

    def set_Style(self):
        self.m_copy_button.setFixedSize(60, 28)
        self.m_copy_button.setStyleSheet(
            "QPushButton{background-color:#108ee9;color:#FFFFFF;font-size:12px;border-radius:4px;}"
            "QPushButton:hover{background-color:#1083E0; border-radius:4px; font-size:12px; color:#FFFFFF;}"
            )
        self.treeWidget_sou.setStyleSheet("QTreeWidget{border-radius:4px;border:1px solid #E5E6E7;}")

        self.m_all_check_file_checkbox.setStyleSheet("QRadioButton{color:#666666;}")
        self.m_save_folder_checkbox.setStyleSheet("QRadioButton{color:#666666;}")

    def set_Thread(self, a_data, a_queue, a_signal, a_event):
        t_copy_fail = ""
        t_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        if self.m_save_folder_checkbox.isChecked():
            t_kep = True
        else:
            t_kep = False
        t_id_list = a_data[0]
        filebox_id_list = a_data[1]
        t_class_work = a_data[2]
        t_des_dir = a_data[3]
        t_no_list = a_data[4]
        for t_work_id in t_id_list:
            for filebox_id in filebox_id_list:
                t_class_work.init_with_id(t_work_id)
                filebox_data = t_class_work.get_filebox_with_filebox_id(filebox_id)
                if type(filebox_data) == dict:
                    t_rule_list = filebox_data["rule"]
                    t_path = filebox_data["path"]
                    re_list = self.change_to_regexp_list(t_rule_list)
                    if self.m_all_check_file_checkbox.isChecked():
                        if os.path.exists(t_path):
                            t_list = ct.file().get_path_list(t_path, re_list)
                            for i in t_list:
                                if os.path.isdir(unicode(i)) and unicode(
                                        os.path.basename(com_replace_path(i))).lower() == "history":
                                    pass
                                elif unicode(os.path.basename(com_replace_path(i))).lower() in t_no_list:
                                    pass
                                else:
                                    t_copy_fail = com_copy([i], t_des_dir, a_fail_str=t_copy_fail,
                                                           a_work_log_signal=a_signal, a_keep_structure=t_kep,
                                                           a_time=t_time, a_is_folder_son=True)
                    else:
                        if os.path.exists(t_path):
                            t_list = ct.file().get_path_list(t_path, re_list)
                            t_new_list = []
                            for i in t_list:
                                if unicode(os.path.basename(com_replace_path(i))).lower() in t_no_list:
                                    continue
                                if os.path.isdir(unicode(i)) and unicode(os.path.basename(com_replace_path(i))).lower() == "history":
                                    continue
                                if unicode(os.path.basename(com_replace_path(i))).lower() == "thumbs.db":
                                    continue
                                else:
                                    t_new_list.append(com_replace_path(i))
                            t_new_list = self.sorted(t_new_list, True)
                            if len(t_new_list) > 0:
                                t_sou = t_new_list[0]
                            else:
                                t_sou = ''
                            if unicode(t_sou).lower().strip() != "":
                                t_copy_fail = com_copy([t_sou], t_des_dir, a_fail_str=t_copy_fail,
                                                       a_work_log_signal=a_signal, a_keep_structure=t_kep,
                                                       a_time=t_time, a_is_folder_son=True)
        a_signal.emit("log", u"Info:复制结束", True)
        if t_copy_fail == "":
            a_signal.emit("info", u"完成", True)
            a_event.wait()
        else:
            a_signal.emit("error", u"以下复制失败:\n" + unicode(t_copy_fail), False)
            a_event.wait()
            a_signal.emit("QPushButton", "True", True)

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

    # ----------------------------------------call-------------------------------------
    def is_error(self):
        self.m_filebox_id_list = []
        self.m_pipeline_list = []
        for i in range(self.treeWidget_sou.topLevelItemCount()):
            top_item = self.treeWidget_sou.topLevelItem(i)
            for n in range(top_item.childCount()):
                item = top_item.child(n)
                if item.checkState(0) == Qt.Checked:
                    self.m_filebox_id_list.append(unicode(item.data(0, 32)))
                    self.m_pipeline_list.append(unicode(item.parent().text(0)))
        if len(self.m_filebox_id_list) == 0:
            message().error(u"请选择需要复制的文件筐!", False)
            return False
        return True

    def change_to_regexp_list(self, file_rule_list):
        t_list = []
        if isinstance(file_rule_list, list):
            for rule in file_rule_list:
                t_list.append(unicode(rule).strip().replace("#", "[0-9]").replace("?", "[a-zA-Z]"))
            return t_list

    # ----------------------------------------slot-------------------------------------
    def slt_add_log(self, a_data):
        try:
            if str(self.k_log_show).lower() == "y":
                self.m_work_log.slt_add_log(a_data)
        except:
            pass

    def slt_copy(self):
        if self.is_error() == False:
            return
        t_des_dir = QFileDialog.getExistingDirectory(self, u"请选择目录", "",
                                                     QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        t_des_dir = unicode(t_des_dir)
        if t_des_dir.strip().lower() == "":
            return
        try:
            t_copy_fail = ""
            self.m_copy_button.setEnabled(False)
            self.slt_add_log(u"Info:开始复制")
            t_sou_id_list = []
            self.m_pipeline_list = list(set(self.m_pipeline_list))
            t_task_module = self.m_tw.task_module(self.m_database, self.m_module)
            t_task_module.init_with_filter(
                [[self.m_module + ".id", "in", self.m_id_list], "and", ["task.pipeline", "in", self.m_pipeline_list]])
            temp_sou_data = t_task_module.get(["task.id"])
            for sou_data in temp_sou_data:
                t_sou_id_list.append(sou_data["task.id"])
        except:
            self.slt_add_log(u"Error:读取数据库存在错误！")
            message().error(u"读取数据库存在错误!", False)
            self.m_copy_button.setEnabled(True)
            return
        if self.k_not_folder != False and unicode(self.k_not_folder).strip() != '':
            t_no_pack_folder = unicode(self.k_not_folder).lower().split("|")
        else:
            t_no_pack_folder = []
        t_data = [t_sou_id_list, self.m_filebox_id_list, t_task_module, t_des_dir, t_no_pack_folder]
        self.m_work_log.run(self.set_Thread, t_data, self.m_copy_button)

    def slt_close(self):
        sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = pack_file_widget()
    sys.exit(app.exec_())