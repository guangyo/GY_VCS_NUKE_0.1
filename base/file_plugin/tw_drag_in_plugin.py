# coding:utf-8
"""
  Purpose: 系统的拖入文件框的插件集合
"""
import os
import sys
import traceback
import shutil

t_base_path = unicode(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/")
t_cgtw_path = unicode(os.path.dirname(t_base_path)) + '/cgtw'
if t_base_path not in sys.path:
    sys.path.append(t_base_path)
if t_cgtw_path not in sys.path:
    sys.path.append(t_cgtw_path)
try:
    from cgtw import *
    import ct_plu
    import ct
except Exception, e:
    print traceback.format_exc()


# ct_base类名是固定的
class ct_base(ct_plu.extend):
    def __init__(self):
        ct_plu.extend.__init__(self)  # 继承

    def drag_image_get_thumbnail(self, a_argv, a_tw):
        """
        Author:    黄骁颖
        Purpose:   拖入图片生成缩略图
        Created:   2018-07-03

        文件筐插件,拖入图片/右键选择图片(可以选择/拖入文件夹):
        0.  action: drag_image_get_thumbnail  (必填)
        1:  allow_format,    允许格式           ex: .png|.tif   key可以不填写
        2:  ban_format,      禁止格式           ex: .jpg|.dpx   key可以不填写
        3:  image_sign,      生成缩略图字段标识  ex: shot.image  key可以不填写,默认为task.image
        4:  des_file_sign    拷贝到目标目录标识  ex: maya_work   key可以不填写
        5:  is_get_folder    是否查询目录内的图片ex: Y/N         key可以不填写
        """
        try:

            INFO_FIELD_SIGN = 1  # 信息模块标志
            TASK_FIELD_SIGN = 2  # 制作模块标志
            
            t_argv     = a_argv
            t_tw       = a_tw
            t_database = t_argv.get_sys_database()
            t_id_list  = t_argv.get_sys_id()

            t_drag_file_list = t_argv.get_sys_file()
            t_module         = t_argv.get_sys_module()
            t_module_type    = t_argv.get_sys_module_type()

            k_allow_format  = t_argv.get_argv_key("allow_format")  # 允许格式
            k_ban_format    = t_argv.get_argv_key("ban_format")  # 禁止格式
            k_image_sign    = t_argv.get_argv_key("image_sign")  # 生成缩略图字段标识
            k_des_file_sign = t_argv.get_argv_key("des_file_sign")  # 拷贝到目标目录标识
            k_is_get_folder = t_argv.get_argv_key("is_get_folder")  # 是否要查询目录内的图片


            # ------配置缩略图字段标识处理
            t_image_sign_type = TASK_FIELD_SIGN
            t_image_sign      = "task.image"  # 默认为制作的缩略图
            
            if k_image_sign != False and str(k_image_sign).strip() != "":
                if len(k_image_sign.split(".")) == 2:
                    if k_image_sign.split(".")[0] == "task":
                        t_image_sign_type = TASK_FIELD_SIGN
                        t_image_sign = k_image_sign
                    elif k_image_sign.split(".")[0] == t_module:
                        t_image_sign_type = INFO_FIELD_SIGN
                        t_image_sign = k_image_sign
                    else:
                        return self.ct_false(u"需要更新的缩略图字段标识错误!")
                else:
                    return self.ct_false(u"需要更新的缩略图字段标识错误!")
                

            if t_module_type == 'task'  :
                t_image_sign_type = TASK_FIELD_SIGN
            elif t_module_type == 'info':
                t_image_sign_type = INFO_FIELD_SIGN          
                    
           
            # ------允许格式处理
            t_allow_format = False
            if k_allow_format != False and str(k_allow_format).strip() != "":
                t_allow_format = k_allow_format.split("|")

            # ------禁止格式处理
            t_ban_format = False
            
            if k_ban_format != False and str(k_ban_format).strip() != "":
                t_ban_format = k_ban_format.split("|")

            # ------获取文件list处理
            
            if k_is_get_folder != False and unicode(k_is_get_folder).strip().lower() == "y":
                t_new_list = []
                for i in t_drag_file_list:
                    if os.path.isdir(i):
                        lists = []
                        for i in ct.file().get_path_list(i):
                            if i.strip().lower().find("thumbs.db") == -1 and i.strip().lower().find(".ini") == -1:
                                lists.append(i)
                        if len(lists) > 0:
                            t_new_list.append(lists[0])
                    else:                      
                        t_new_list.append(i)

            else:
                t_new_list = t_drag_file_list

            # ------处理需要生成的缩略图的文件格式
            t_image_list = []
            if t_allow_format != False:
                for temp in t_new_list:
                    if os.path.isfile(temp.replace("\\", "/")) and os.path.splitext(temp.replace("\\", "/"))[-1] in t_allow_format:
                        t_image_list.append(temp.replace("\\", "/"))
            else:
                if t_ban_format != False:
                    for temp in t_new_list:
                        if os.path.isfile(temp.replace("\\", "/")) and not os.path.splitext(temp.replace("\\", "/"))[-1] in t_ban_format:
                            t_image_list.append(temp.replace("\\", "/"))
                else:
                    t_image_list = t_new_list
            


            # -----开始生成缩略图
           
            if t_image_sign_type == TASK_FIELD_SIGN:
                try:
                    t_tw.task_module(t_database, t_module, t_id_list).set_image(t_image_sign, t_image_list)
                except Exception,e:
                    return self.ct_false(u"生成缩略图失败%s"%str(unicode(e)))


            elif t_image_sign_type == INFO_FIELD_SIGN:
                try:
                    t_info_id = t_tw.info_module(t_database, t_module, t_id_list).get([t_module + ".id"])[0][
                        t_module + ".id"]
                    t_tw.info_module(t_database, t_module, [t_info_id]).set_image(t_image_sign, t_image_list)

                except Exception,e:
                    return self.ct_false(u"生成缩略图失败")
                    
            # ------是否拷贝文件
            if k_des_file_sign != False and str(k_des_file_sign).strip() != "":
                try:
                    t_des_path = t_tw.task_module(t_database, t_module, t_id_list).get_dir([k_des_file_sign])[0][
                        k_des_file_sign]
                except Exception, e:
                    return self.ct_false(u"读取目标目录失败!")
                # -------------------------
                try:
                    for i in t_drag_file_list:
                        t_des_file_path = t_des_path + "/" + os.path.basename(i)
                        #===============骁颖==2018.06.15===================== 
                        #shutil.copy(i, t_des_file_path)
                        ct.file().copy_file(i, t_des_file_path)
                        #===============骁颖==2018.06.15===================== 
                        if os.path.exists(t_des_file_path) == False:

                            return self.ct_false(u'拷贝失败:\n')
                except Exception, e:
                    return self.ct_false(u'没有权限或目录标志不存在:\n')
                # -------------------------
            return self.ct_true()  # 正确返回true,如果要给后面的插件传递值的话。在这边加上
        except Exception, e:
            # print traceback.format_exc()
            return self.ct_false(u'插件执行失败:\n%s'%str(unicode(e)))
        

    def drag_mov_get_thumbnail(self, a_argv, a_tw):
        """
        Author:  黄骁颖
        Purpose: 拖入mov生成缩略图并检查帧数
        Created: 2018-07-03

        文件筐插件,拖入mov/右键mov(可以选择/拖入文件夹):
        0.  action: drag_mov_get_thumbnail  (必填)
        1:  is_get_thumbnail, 是否更新缩略图      ex: Y/N           key可以不填写
        2:  is_update_frame,  是否更新帧数         ex: Y/N          key可以不填写
        3:  is_check_frame,   是否检查帧数         ex: Y/N          key可以不填写
        4:  is_get_folder,    是否查询目录里的文件         ex: Y/N   key可以不填写
        5:  image_sign,       生成缩略图字段标识   ex: shot.image    key可以不填写
        6:  des_file_sign,    拷贝到目标目录标识   ex: maya_work     key可以不填写
        7： frame_rate,       帧率               ex:24            key可以不填写
        8:  width             宽                                  key可以不填写
        9:  height            高                                  key可以不填写
        """
        try:
            t_tw   = a_tw
            t_argv = a_argv
            k_is_get_thumanil = t_argv.get_argv_key("is_get_thumbnail")
            k_is_update_frame = t_argv.get_argv_key("is_update_frame")
            k_is_check_frame  = t_argv.get_argv_key("is_check_frame")
            k_is_get_folder   = t_argv.get_argv_key("is_get_folder")
            k_image_sign      = t_argv.get_argv_key("image_sign")
            k_des_file_sign   = t_argv.get_argv_key("des_file_sign")
            k_frame_rate      = t_argv.get_argv_key("frame_rate")
            k_width       = t_argv.get_argv_key("width")
            k_height      = t_argv.get_argv_key("height")
            t_database    = t_argv.get_sys_database()
            t_id_list     = t_argv.get_sys_id()
            t_module      = t_argv.get_sys_module()
            t_module_type = t_argv.get_sys_module_type()
            t_sou_list    = t_argv.get_sys_file()  # 取固定的系统数据
    
            INFO_FIELD_SIGN = 1  # 信息模块标识
            TASK_FIELD_SIGN = 2  # 制作模块标识
    
            #t_fail_list = []

    
    
            # 获取文件list处理
            if k_is_get_folder != False and unicode(k_is_get_folder).strip().lower() == "y":
                t_new_list = []
                for i in t_sou_list:
                    if os.path.isdir(i):
                        t_new_list = t_new_list + ct.file().get_path_list(i)
                    else:
                        t_new_list.append(i)
            else:
                t_new_list = t_sou_list
    
            for i in t_new_list:
                if os.path.isfile(i):
                    t_fileUrl = i.replace("\\", "/")
                    # 获取视频信息及缩略图------------------------------------
                    try:
                        t_avi_info = ct.mov().get_avi_info(i)
                        t_fate     = t_avi_info["FrameRate"]
                        t_frame    = t_avi_info["FrameCount"]
                        t_avi_thumanil = ct.com().get_tmp_path() + "/" + ct.com().uuid() + ".png"
                        ct.mov().get_mov_thumbnail(i, t_avi_thumanil.replace("\\", "/"))
                        t_thumanil      = t_avi_thumanil.replace("\\", "/")
                        t_avi_info_dict = t_avi_info
                    except Exception, e:
                        return self.ct_false(t_fileUrl + u": 获取视频信息失败")
                        #t_fail_list.append(t_fileUrl + u": 获取视频信息失败")
                        #continue
                    # 检查宽高-----------------------------------------------
                    try:
                        if str(k_width).strip() != "" and k_width != False:
                            if t_avi_info_dict != False and t_avi_info_dict.has_key("Width"):
                                if int(k_width) != int(t_avi_info_dict["Width"]):
                                    return self.ct_false(t_fileUrl + u": 宽度不正确:-----系统宽度-----mov宽度\n" + u"-----" + str(int(k_width)) + u"-----" + str(int(t_avi_info_dict["Width"])))
                                    #t_fail_list.append(t_fileUrl + u": 宽度不正确:-----系统宽度-----mov宽度\n" + u"-----" + str(int(k_width)) + u"-----" + str(int(t_avi_info_dict["Width"])))
                                    #continue
                            else:
                                return self.ct_false(t_fileUrl + u": 读取mov分辨率出错")
                                #t_fail_list.append(t_fileUrl + u": 读取mov分辨率出错")
                                #continue
    
                        if str(k_height).strip() != "" and k_height != False:
                            if t_avi_info_dict != False and t_avi_info_dict.has_key("Heigh"):
                                if int(k_height) != int(t_avi_info_dict["Heigh"]):
                                    return self.ct_false(t_fileUrl + u": 高度不正确:-----系统高度-----mov高度\n" + u"-----" + str(int(k_height)) + u"-----" + str(int(t_avi_info_dict["Heigh"])))
                                    #t_fail_list.append(t_fileUrl + u": 高度不正确:-----系统高度-----mov高度\n" + u"-----" + str(int(k_height)) + u"-----" + str(int(t_avi_info_dict["Heigh"])))
                                    #continue
                            else:
                                return self.ct_false(t_fileUrl + u": 读取mov分辨率出错")
                                #t_fail_list.append(t_fileUrl + u": 读取mov分辨率出错")
                                #continue
                    except Exception, e:
                        return self.ct_false(t_fileUrl + u": 检查分辨率发生未知错误!")
                        #t_fail_list.append(t_fileUrl + u": 检查分辨率发生未知错误!")
                        #continue
    
                    # 检查帧率----------------------------------------------
                    try:
                        if str(k_frame_rate).strip() != "" and k_frame_rate != False:
                            if int(float(k_frame_rate)) != int(float(t_fate)):
                                return self.ct_false(t_fileUrl + u": 帧率不正确:-----系统帧率-----mov帧率\n" + u"-----" + str(
                                    int(float(k_frame_rate))) + u"-----" + str(int(float(t_fate))))
                                #t_fail_list.append(t_fileUrl + u": 帧率不正确:-----系统帧率-----mov帧率\n" + u"-----" + str(
                                    #int(float(k_frame_rate))) + u"-----" + str(int(float(t_fate))))
                                #continue
                    except Exception, e:
                        return self.ct_false(t_fileUrl + u": 检查帧率发生未知错误!")
                        #t_fail_list.append(t_fileUrl + u": 检查帧率发生未知错误!")
                        #continue
    
                    # 检查帧数----------------------------------------------
                    if str(k_is_check_frame).strip().lower() == "y":
                        try:
                            t_info_id = t_tw.task_module(t_database, t_module, t_id_list).get([t_module + ".id"])[0][
                                t_module + ".id"]
                            t_frmaes = t_tw.info_module(t_database, "shot", [t_info_id]).get(["shot.frame"])[0][
                                "shot.frame"]
                            if t_frmaes == "None" or t_frmaes == False or t_frmaes == "" or t_frmaes == None:
                                t_frmaes = 0
                            if int(t_frame) != int(t_frmaes):
                                return self.ct_false(t_fileUrl + u": 帧数不正确:-----系统帧数-----mov帧数\n" + u"-----" + str(int(t_frmaes)) + u"-----" + str(int(t_frame)))
                                #t_fail_list.append(t_fileUrl + u": 帧数不正确:-----系统帧数-----mov帧数\n" + u"-----" + str(
                                    #int(t_frmaes)) + u"-----" + str(int(t_frame)))
                                #continue
                        except Exception, e:
                            return self.ct_false(t_fileUrl + u": 检查/更新帧数,发生未知错误!")
                            #t_fail_list.append(t_fileUrl + u": 检查/更新帧数,发生未知错误!")
                            #continue
    
                            # 是否更新帧数
                    if str(k_is_update_frame).strip().lower() == "y":
                        try:
                            t_info_id = t_tw.task_module(t_database, t_module, t_id_list).get([t_module + ".id"])[0][
                                t_module + ".id"]
                            t_tw.info_module(t_database, "shot", [t_info_id]).set({"shot.frame": t_frame})
                        except Exception, e:
                            return self.ct_false(t_fileUrl + u": 更新帧数,发生未知错误!")
                            #t_fail_list.append(t_fileUrl + u": 更新帧数,发生未知错误!")
                            #continue
                    
                    # 是否更新缩略图-----------------------------------------
                    if str(k_is_get_thumanil).strip().lower() == "y":
                        # 配置缩略图字段标识处理
                        t_image_sign_type = TASK_FIELD_SIGN
                        t_image_sign = "task.image"  # 默认为制作的缩略图
                        #return self.ct_false(str(k_image_sign)+"|"+str(t_image_sign_type)+str(t_image_sign))
                        if k_image_sign != False and str(k_image_sign).strip() != "":
                            if len(k_image_sign.split(".")) == 2:
                                if k_image_sign.split(".")[0] == "task":
                                    t_image_sign_type = TASK_FIELD_SIGN
                                    t_image_sign = k_image_sign
                                elif k_image_sign.split(".")[0] == t_module:
                                    t_image_sign_type = INFO_FIELD_SIGN
                                    t_image_sign = k_image_sign
                                else:
                                    return self.ct_false(t_fileUrl + u": 需要更新的缩略图字段标识错误!")
                                    #t_fail_list.append(t_fileUrl + u": 需要更新的缩略图字段标识错误!")
                                    #continue
                            else:
                                return self.ct_false(t_fileUrl + u": 需要更新的缩略图字段标识错误!")
                                #t_fail_list.append(t_fileUrl + u": 需要更新的缩略图字段标识错误!")
                                #continue
                        if t_module_type == 'task':
                            t_image_sign_type = TASK_FIELD_SIGN
                        elif t_module_type == 'info':
                            t_image_sign_type = INFO_FIELD_SIGN
                            
                        # 开始生成缩略图
    
                        
                        if t_image_sign_type == TASK_FIELD_SIGN:
                            try:
                                t_tw.task_module(t_database, t_module, t_id_list).set_image(t_image_sign, t_thumanil)
                            except Exception, e:
                                return self.ct_false(t_fileUrl + u": 生成缩略图失败!%s"%str(unicode(e)))
                                #t_fail_list.append(t_fileUrl + u": 生成缩略图失败!%s"%str(unicode(e)))
                                #continue
                        elif t_image_sign_type == INFO_FIELD_SIGN:
                            try:
                                t_info_id = t_tw.info_module(t_database, t_module, t_id_list).get([t_module + ".id"])[0][
                                    t_module + ".id"]
                                t_tw.info_module(t_database, t_module, [t_info_id]).set_image(t_image_sign, t_thumanil)
                            except Exception, e:
                                return self.ct_false(t_fileUrl + u": 生成缩略图失败!%s"%str(unicode(e)))
                                #t_fail_list.append(t_fileUrl + u": 生成缩略图失败!%s"%str(unicode(e)))
                                #continue
    
                    # 是否拷贝文件-------------------------------------------
                    if k_des_file_sign != False and str(k_des_file_sign).strip() != "" and str(
                            k_des_file_sign).strip() != "None":
                        try:
                            t_des_path = t_tw.task_module(t_database, t_module, t_id_list).get_dir([k_des_file_sign])[0][
                                k_des_file_sign]
                        except Exception, e:
                            return self.ct_false(t_fileUrl + u": 读取目标目录失败!")
                            #t_fail_list.append(t_fileUrl + u": 读取目标目录失败!")
                            #continue
                            # -------------------------
                        try:
                            #===============骁颖==2018.06.15===================== 
                            #shutil.copyfile(i, t_des_path + "/" + os.path.basename(i))
                            ct.file().copy_file(i, t_des_path + "/" + os.path.basename(i))
                            
                            #===============骁颖==2018.06.15===================== 
                        except Exception, e:
                            return self.ct_false(t_fileUrl + u": 拷贝失败!")
                            #t_fail_list.append(t_fileUrl + u": 拷贝失败!")
                            #continue
                        # -------------------------
                else:
                    return self.ct_false(i + u": 不是文件!")
                    #t_fail_list.append(i + u": 不是文件!")
                    #continue
            #if t_fail_list != []:
                #return self.ct_false('\n'.join(t_fail_list))
        
        except Exception,e:
            return self.ct_false(u'插件执行失败:\n%s'%str(unicode(e)))
    def image_stitching(self, a_argv, a_tw):
        # 仕煌
        '''
        多张图片拼接成新图片，#图片拼接，并生成一个新的图片,不复制原先的图片
        0.  action : image_stitching  (必填)
        '''
        t_argv = a_argv
        t_sou_list = t_argv.get_sys_file()  # 取固定的系统数据
        t_folder = t_argv.get_sys_folder()  # 取文件框对应的目录.
        if t_folder == False or str(t_folder) == "":
            return self.ct_false(u"取目录失败")
        if os.path.exists(t_folder) == False:
            return self.ct_false(u"目录(" + t_folder + u")未创建")

        if isinstance(t_sou_list, list) == False:
            return self.ct_false(u"提交文件类型错误")
        if len(t_sou_list) <= 0:
            return self.ct_false(u"没有找到提交文件")

        try:
            des_file_path = ""
            total = ""
            t_uuid_file_list = []
            t_sou_list.sort()
            for i in t_sou_list:
                if des_file_path == "":
                    des_file_path = t_folder + "/" + os.path.basename(i)
                if ct.com().exist_chinese(i):  # 是否存在中文命名
                    temp_file = ct.com().get_tmp_path() + "/" + str(ct.com().uuid()) + "." + os.path.splitext(i)[1]
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    #===============骁颖==2018.06.15=====================  
                    #shutil.copyfile(i, temp_file)
                    ct.file().copy_file(i, temp_file)
                    #===============骁颖==2018.06.15=====================  
                    
                    t_uuid_file_list.append(temp_file)
                    total = total + ' ' + '"' + temp_file + '"'
                else:
                    total = total + ' ' + '"' + i + '"'
            res = self.__convert_image_stitching(total, os.path.splitext(des_file_path)[1])
            if res == False:
                return self.ct_false(u"调用转换命令，拼接失败")
            else:
                if os.path.exists(des_file_path):
                    os.remove(des_file_path)
                    
                #===============骁颖==2018.06.15===================== 
                #shutil.copyfile(res, des_file_path)
                ct.file().copy_file(res, des_file_path)
                #===============骁颖==2018.06.15=====================                  
            for i in t_uuid_file_list:
                os.remove(i)

            # 停止后续的插件/或者动作
            return self.ct_stop_next()
        except Exception, e:
            return self.ct_false(u"拼接图片失败")

    def drag_copy_file_to_folder_sign(self, a_argv, a_tw):
        """
        Author:    黄骁颖
        Created:   2018-03-23

        拷贝拖入文件到目录标识:
        0. action    :    drag_copy_file_to_folder_sign
        1:  folder_sign,            目录标识
        2:  replace_str,     改名替换字符（可空）           比如work,ok|v#,finish 意思是将work替换成ok,并且将v1替换成finish
        3. a_is_exist_file_move_to_history     （可空）目标存在文件是否移动到历史(/history/2018-11-11-23-01-01)    N/Y
        """

        t_des_type = "folder"
        t_des_sign = a_argv.get_argv_key("folder_sign")
        if t_des_sign == False or t_des_sign.strip() == "":
            return self.ct_false(u"获取文件框标识失败")

        t_replace_str = a_argv.get_argv_key("replace_str")
        if t_replace_str == False or t_replace_str.strip() == "":
            t_replace_str = ""

        t_is_exist_move_to_history = a_argv.get_argv_key("is_exist_file_move_to_history")
        if t_is_exist_move_to_history == False or t_is_exist_move_to_history.strip() == "":
            t_is_exist_move_to_history = ''

        t_error = self.__drag_copy_file(a_argv, a_tw, t_des_type, t_des_sign, t_replace_str, t_is_exist_move_to_history)
        if t_error != "":
            return self.ct_false(t_error)

    def drag_copy_file_to_filebox_sign(self, a_argv, a_tw):
        """
        Author:    黄骁颖
        Created:   2018-03-23

        拷贝拖入文件到目录标识:
        0.  action   :  drag_copy_file_to_filebox_sign
        1:  filebox_sign,            文件框标识
        2:  replace_str,     改名替换字符（可空）                  比如work,ok|v#,finish 意思是将work替换成ok,并且将v1替换成finish
        3.  is_exist_file_move_to_history     （可空）目标存在文件是否移动到历史(/history/2018-11-11-23-01-01)    N/Y
        """
        t_des_type = "filebox"
        t_des_sign = a_argv.get_argv_key("filebox_sign")
        if t_des_sign == False or t_des_sign.strip() == "":
            return self.ct_false(u"获取文件框标识失败")

        t_replace_str = a_argv.get_argv_key("replace_str")
        if t_replace_str == False or t_replace_str.strip() == "":
            t_replace_str = ""

        t_is_exist_move_to_history = a_argv.get_argv_key("is_exist_file_move_to_history")
        if t_is_exist_move_to_history == False or t_is_exist_move_to_history.strip() == "":
            t_is_exist_move_to_history = ""

        t_error = self.__drag_copy_file(a_argv, a_tw, t_des_type, t_des_sign, t_replace_str, t_is_exist_move_to_history)
        if t_error != "":
            return self.ct_false(t_error)

    # -----------------------------------------------内部调用-----------------------------

    def __convert_image_stitching(self, total_image, t_format):
        out_put = ct.com().get_tmp_path() + "/image_stitching" + t_format
        convert_path = t_cgtw_path + "/convert.exe"
        if os.path.exists(convert_path) == False:
            return self.ct_false(u"( " + convert_path + u" ) 文件不存在")
        cmd = '"' + convert_path + '" ' + total_image + " -gravity south +append " + '"' + out_put + '"'
        ct.com().exec_cmd(cmd)
        if os.path.exists(out_put) == False or os.path.getsize(out_put) <= 0:
            return False
        else:
            return out_put

    def __re_rule(self, new_rule):  # 新正则规则
        return new_rule.replace("#", "\d").replace("?", "[a-zA-Z]").replace("*", ".")

    def __drag_copy_file(self, a_argv, a_tw, a_des_type, a_des_sign, a_replace_str, a_is_exist_move_to_history):
        try:
            t_argv = a_argv
            t_tw = a_tw
            t_module = t_argv.get_sys_module()
            t_id_list = t_argv.get_sys_id()
            t_database = t_argv.get_sys_database()
            t_sou_file_list = t_argv.get_sys_file()  # 取拖入文件列表
            if t_argv.get_filebox_key("type")=="drag_after_plugin":
                t_sou_file_list=t_argv.get_sys_des_file()

            t_module_type = t_argv.get_sys_module_type()
            if t_module_type == "task":
                t_module_class = t_tw.task_module(t_database, t_module, t_id_list)
            else:
                t_module_class = t_tw.info_module(t_database, t_module, t_id_list)

        except Exception, e:
            return u"数据库读取失败"

        if t_sou_file_list == False or t_sou_file_list == []:
            return u"请拖入文件"

        try:
            if a_des_type == "folder":
                t_des_dir = t_module_class.get_dir([a_des_sign])[0][a_des_sign]
            elif a_des_type == "filebox":
                t_des_dir = t_module_class.get_filebox_with_sign(a_des_sign)['path']
            else:
                return u"des_type错误"
        except:
            return u"读取目标目录失败"

        t_error = ""
        for t_sou_file_path in t_sou_file_list:  # 循环拖入文件列表
            t_error += self.__copy_files_sign(t_des_dir, t_sou_file_path, a_is_exist_move_to_history, a_replace_str)
        return t_error

    def __copy_files_sign(self, a_des_dir, a_sou_file_path, a_is_move_history, a_replace_str):
        """
        复制移动文件或文件夹
        """

        t_sou_file_name = os.path.basename(a_sou_file_path)
        t_des_file_name = t_sou_file_name
        # ---a_replace_str 重命名
        try:
            if a_replace_str != False and a_replace_str.strip() != "":
                t_replace_list = a_replace_str.split("|")
                for i in t_replace_list:
                    replace_list = i.split(",")
                    if len(replace_list) == 2:
                        t_des_file_name = re.sub(self.__re_rule(replace_list[0]), replace_list[1], t_des_file_name)
        except:
            # print traceback.print_exc()
            return u"重命名文件异常 --> " + t_sou_file_name + "\n"

        t_des_file_path = unicode(a_des_dir + '/' + t_des_file_name).replace("\\", "/")  #

        t_sou_path_list = []
        # --判断是否是文件夹'
        if os.path.isdir(a_sou_file_path):
            t_sou_path_list = ct.file().get_file_with_walk_folder(a_sou_file_path)
        else:
            t_sou_path_list = [a_sou_file_path]

        date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        try:
            for i in t_sou_path_list:
                des_path = unicode(i).replace("\\", "/").replace(a_sou_file_path, t_des_file_path)
                if os.path.exists(des_path) and unicode(a_is_move_history).strip().lower() == "y":
                    t_history_file_path = unicode(des_path).replace(a_des_dir + "/",
                                                                    a_des_dir + '/history/' + date + "/")
                    if not os.path.exists(os.path.dirname(t_history_file_path)):
                        os.makedirs(os.path.dirname(t_history_file_path))  # --创建历史文件夹
                    shutil.move(des_path, t_history_file_path)

                if not os.path.exists(os.path.dirname(des_path)):
                    os.makedirs(os.path.dirname(des_path))  # --创建历史文件夹

                # ------------------------骁颖-----------------------
                
                #===============骁颖==2018.06.15================== 
                #shutil.copyfile(i, des_path)
                ct.file().copy_file(i, des_path)
                            
                #try:
                    #shutil.copystat(i, des_path)
                #except:
                    #pass
                 #===============骁颖==2018.06.15================== 
                 
                # shutil.copy2(i, des_path )
                # ------------------------骁颖-----------------------
        except Exception, e:
            # print traceback.print_exc()
            return u"复制失败 " + a_sou_file_path + " --> " + t_des_file_path + "\n"

        return ""

    # -----------------------------------------------内部调用-----------------------------

    # 重写run,外部调用
    def run(self, a_dict_data):
        try:
            t_argv = ct_plu.argv(a_dict_data)
            t_tw = tw()
            t_action = t_argv.get_argv_key("action")
            if t_action == "drag_image_get_thumbnail":
                return self.drag_image_get_thumbnail(t_argv, t_tw)

            elif t_action == "drag_mov_get_thumbnail":
                return self.drag_mov_get_thumbnail(t_argv, t_tw)

            elif t_action == "image_stitching":
                return self.image_stitching(t_argv, t_tw)

            elif t_action == "drag_copy_file_to_folder_sign":
                return self.drag_copy_file_to_folder_sign(t_argv, t_tw)

            elif t_action == "drag_copy_file_to_filebox_sign":
                return self.drag_copy_file_to_filebox_sign(t_argv, t_tw)
            else:
                return self.ct_false(u"未查询到action对应插件!")



        except Exception, e:
            # print traceback.format_exc()
            return self.ct_false(traceback.format_exc())


if __name__ == "__main__":
    # 调试数据,前提需要在拖入进程中右键菜单。发送到调试
    t_debug_argv_dict = ct_plu.argv().get_debug_argv_dict()
    print ct_base().run(t_debug_argv_dict)
