# -*- coding: utf-8 -*-
#Author:王晨飞
#Time  :2017-12-19
#Describe:拷贝文件的 目录到目录的整理,这个子线程可以使用
#         覆盖文件,查询规则完全匹配
#         CgTeamWork V5整合
import os
import re
import sys
import json
import time
import shutil
G_cgtw_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__.replace("\\","/"))))+"/cgtw"
if not G_cgtw_path in sys.path:
    sys.path.append(G_cgtw_path)
import ct

#排序
def __sorted(lis, is_reverse=False):  
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

def __call_add_log(a_work_log_signal, a_work_log_function, a_message):
    if a_work_log_signal!=False:
        a_work_log_signal.emit("log", a_message, True )
    elif a_work_log_function!=False:
        a_work_log_function( a_message )
def __call_copy_fail(a_fail_str, a_message, a_sou_list, a_des_list):
    if a_fail_str!=False:
        return a_fail_str + "%s:%s---->%s\n"%(a_message, unicode(json.dumps(a_sou_list)),unicode(json.dumps(a_des_list)))
    return a_fail_str
def com_is_match_rule(a_file, a_rule_list, a_fully_conformed = False):
    #查询是否符合命名规则
    a_file_name = os.path.basename(a_file)
    for rule in a_rule_list:
        if re.match(rule, a_file_name):
            if a_fully_conformed:
                temp = re.match(rule, a_file_name)
                if len(a_file_name)==len(temp.group(0)):
                    return True
            else:
                return True
    return False
def com_str_to_rule(a_str, a_has_foramt = False):
    #从cgteamwork中取到的不规则的命名规则,转换为正则表达式
    t_rule_list = []
    for i in unicode(a_str).split("|"):
        if a_has_foramt:
            t_rule_list.append( i.replace("#", "\d").replace("?","[a-zA-Z]") )
        else:
            t_rule_list.append( i.replace("#", "\d").replace("?","[a-zA-Z]").replace("*",".*") )
    return t_rule_list
def com_rule_to_str(a_str,a_rule_list):
    #根据规则,查询字符串中符合规则的字符串
    t_str_list = []
    for i in a_rule_list:
        if re.findall(i, a_str):
            t_str_list.append( re.findall(i, a_str)[0] )
    return t_str_list
def com_replace_path(a_path):
    t_path = a_path.replace("\\","/")
    if t_path[-1]=="/":
        t_path = t_path[0:-1]
        if t_path[-1]!="/":
            return t_path
        else:
            return com_replace_path(t_path)
    else:
        return t_path
def com_copy(a_sou_argv, a_des_argv, a_time=False, a_add_str=False, a_replace_str=False, a_work_log_signal=False, a_work_log_function=False, a_fail_str=False, a_keep_structure=False, a_is_folder_son=False, a_is_cover=False, a_is_copy_all='Y'):
    #-----------源---------目标----------时间-------改名追加字符串------改名替换字符串-----------工作日志信号-------------工作日志类-----------------失败字符串------是否保存目录架构--------源的目录是否是目录的子层--是否覆盖----------是否拷贝全部文件('N'为拷贝最大版本)
    #-------->时间
    if a_time==False:
        t_time = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    else:
        t_time = a_time

        
    #--------源与目标处理
    t_sou_list      = []
    t_des_list      = []
    t_history_list  = []

    if not isinstance(a_sou_argv, list) and not isinstance(a_des_argv, list):
        #-------->str,str(字符串->字符串),这时源,目标为同一类型!不考虑保持目录结构!
        a_sou_argv = com_replace_path( a_sou_argv )
        a_des_argv = com_replace_path( a_des_argv )
        if os.path.exists(a_sou_argv.replace("\\","/")):
            temp_sou = a_sou_argv.replace("\\","/")
            temp_des = a_des_argv.replace("\\","/")
            if os.path.isfile( temp_sou ):
                temp_history = os.path.join(os.path.dirname(temp_des), "history")
            else:
                temp_history = os.path.join(temp_des, "history")
                if a_is_folder_son:
                    temp_des = os.path.join(a_des_argv.replace("\\","/"), os.path.basename(temp_sou))
            t_sou_list.append(         temp_sou.replace("\\", "/") )
            t_des_list.append(         temp_des.replace("\\", "/") )
            t_history_list.append( temp_history.replace("\\", "/") )

    if isinstance(a_sou_argv, list) and not isinstance(a_des_argv, list):

        #-------->list,str(列表->字符串),这时源做判断,目标为文件夹!考虑保持目录结构!
        a_des_argv = com_replace_path( a_des_argv )
        for temp in a_sou_argv:

            temp = com_replace_path( temp )
            if os.path.exists(temp):

                if a_keep_structure:

                    temp_sou     = temp
                    if os.path.splitdrive(unicode(temp_sou))[0]=="":#mac
                        temp_des = a_des_argv.replace("\\","/") + "/" + temp_sou
                    else:#win
                        temp_des = temp_sou.replace( os.path.splitdrive(unicode(temp_sou))[0] , a_des_argv.replace("\\","/") )
                    temp_history = os.path.join(a_des_argv.replace("\\","/"), "history")
                    t_sou_list.append(         temp_sou.replace("\\", "/") )
                    t_des_list.append(         temp_des.replace("\\", "/") )
                    t_history_list.append( temp_history.replace("\\", "/") )
                else:
   
                    temp_sou     = temp
                    if os.path.isfile(temp_sou):
                        temp_des     = os.path.join(a_des_argv.replace("\\","/"), os.path.basename(temp_sou))
                    else:
                        temp_des     = a_des_argv.replace("\\","/")
                    temp_history = os.path.join(a_des_argv.replace("\\","/"), "history")
                    if a_is_folder_son and os.path.isdir( temp_sou ):
                        temp_des = os.path.join(a_des_argv.replace("\\","/"), os.path.basename(temp_sou))
                    t_sou_list.append(         temp_sou.replace("\\", "/") )
                    t_des_list.append(         temp_des.replace("\\", "/") )
                    t_history_list.append( temp_history.replace("\\", "/") )

    if isinstance(a_sou_argv, list) and isinstance(a_des_argv, list):

        #-------->list,list(列表->列表)这时源,目标为同一类型!不考虑保持目录结构!
        for i in range(len(a_sou_argv)):
            if os.path.exists(a_sou_argv[i]):
                temp_sou = com_replace_path( a_sou_argv[i].replace("\\","/") )
                temp_des = com_replace_path( a_des_argv[i].replace("\\","/") )
                if os.path.isfile( temp_sou ):
                    temp_history = os.path.join(os.path.dirname(temp_des), "history")
                else:
                    temp_history = os.path.join(temp_des, "history")
                    if a_is_folder_son:
                        temp_des = os.path.join(temp_des, os.path.basename(temp_sou))
                t_sou_list.append(         temp_sou.replace("\\", "/") )
                t_des_list.append(         temp_des.replace("\\", "/") )
                t_history_list.append( temp_history.replace("\\", "/") )
 
#---------------------------------------------------------------------------骁颖------------------------------------------------------------------------ 
    for s in range(len(t_sou_list)):

        t_sou_file     = t_sou_list[s]
        t_des_file     = t_des_list[s]
        t_history_path = t_history_list[s]
        
        t_sou_file     = com_replace_path( t_sou_file )
        t_des_file     = com_replace_path( t_des_file )   
        t_history_path = com_replace_path( t_history_path )        


        if os.path.isfile( t_sou_file ):#file   -> file
            t_sou_file_list = [t_sou_file.replace("\\","/")]
            t_des_file_list = [t_des_file.replace("\\","/")]
            t_history_lists = [t_history_path.replace("\\","/")]
        else:                  #folder -> folder

            t_sou_file_list = []
            t_des_file_list = []
            t_history_lists = []
            t_choose_max_file = []
            if unicode(a_is_copy_all).strip().lower()!="y":  #最大版本
                for i in os.listdir(t_sou_file): #---过滤Thumbs 和 历史文件夹 
                    if i == 'Thumbs.db':
                        continue
                    if i == u'history' and os.path.isdir(os.path.join(t_sou_file,i).replace('\\','/')):
                        continue
                    try:
                        t_choose_max_file.append( os.path.join(t_sou_file,i).decode("gbk").replace("\\","/") )
                    except Exception,e:
                        t_choose_max_file.append( os.path.join(t_sou_file,i).replace("\\","/") )   

                if len(t_choose_max_file)>0:
                    t_max_file_version = __sorted(t_choose_max_file, True)[0] #排序取最大版本
    
                    if os.path.isdir(t_max_file_version):
                       #----若最大版本是文件夹
                        for i in ct.file().get_file_with_walk_folder(t_max_file_version):
                            try:
                                t_sou_file_list.append( i.decode("gbk").replace("\\","/") )
                                t_des_file_list.append( i.decode("gbk").replace("\\","/").replace(t_sou_file,t_des_file) )
                                t_history_lists.append(  t_history_path.replace("\\","/")  )
                            except Exception,e:
                                t_sou_file_list.append( i.replace("\\","/") )
                                t_des_file_list.append( i.replace("\\","/").replace(t_sou_file,t_des_file) )
                                t_history_lists.append(  t_history_path.replace("\\","/")  ) 
                                
                    else:  #---最大版本不是文件夹
                        try:
                            t_sou_file_list.append( t_max_file_version.decode("gbk").replace("\\","/") )
                            t_des_file_list.append( t_max_file_version.decode("gbk").replace("\\","/").replace(t_sou_file,t_des_file) )
                            t_history_lists.append(  t_history_path.replace("\\","/")  )
                        except Exception,e:
                            t_sou_file_list.append( t_max_file_version.replace("\\","/") )
                            t_des_file_list.append( t_max_file_version.replace("\\","/").replace(t_sou_file,t_des_file) )
                            t_history_lists.append(  t_history_path.replace("\\","/")  )                    
                


                
            else:   #所有文件   

                for i in ct.file().get_file_with_walk_folder( t_sou_file ):

                    if os.path.basename(i) == u'Thumbs.db':
                        continue
                
                    if u'/history' in os.path.dirname(i):
                        continue
                    try:
                        t_sou_file_list.append( i.decode("gbk").replace("\\","/") )
                        t_des_file_list.append( i.decode("gbk").replace("\\","/").replace(t_sou_file,t_des_file) )
                        t_history_lists.append(  t_history_path.replace("\\","/")  )
                    except Exception,e:
                        print unicode(e)
                        t_sou_file_list.append( i.replace("\\","/") )
                        t_des_file_list.append( i.replace("\\","/").replace(t_sou_file,t_des_file) )
                        t_history_lists.append(  t_history_path.replace("\\","/")  )
                        

                
#---------------------------------------------------------------------------骁颖------------------------------------------------------------------------ 
        for s in range(len(t_sou_file_list)):
            
            #-------->改名
            t_des_name   = os.path.splitext(os.path.basename(t_des_file_list[s]))[0]
            t_des_format = os.path.splitext(os.path.basename(t_des_file_list[s]))[1]
            if a_add_str!=False:
                for a_str in a_add_str.split("|"):
                    t_des_name = a_str.replace("*",t_des_name)
            if a_replace_str!=False:
                for a_str in a_replace_str.split("|"):
                    t_des_name = t_des_name.replace(a_str.split(",")[0],a_str.split(",")[1])
            t_des_abc_path = unicode(os.path.join( os.path.dirname(t_des_file_list[s]), t_des_name + t_des_format)).replace("\\","/")
            #-------->移动到历史

            if os.path.exists( t_des_abc_path ) and a_is_cover==False:

                t_history_path_ =  t_des_abc_path.replace(os.path.dirname(t_history_lists[s]), os.path.join(t_history_lists[s],t_time))
                if not os.path.exists( os.path.dirname(t_history_path_) ):
                    os.makedirs( os.path.dirname(t_history_path_) )
                try:
                    #------------------------骁颖-----------------------
                    
                    #===============骁颖==2018.06.15=========================
                    #shutil.copyfile(t_des_abc_path, t_history_path_)       
                    #shutil.copyfile(t_sou_file_list[s], t_des_abc_path)    
                    ct.file().copy_file(t_des_abc_path, t_history_path_)    
                    ct.file().copy_file(t_sou_file_list[s], t_des_abc_path) 
                    
                    
                    
                    #try:
                        #shutil.copystat(t_des_abc_path, t_history_path_)
                        #shutil.copystat(t_sou_file_list[s], t_des_abc_path)
                    #except :
                        #pass
                    #===============骁颖==2018.06.15=========================
                    
                    
                    #shutil.copy2(t_des_abc_path,     t_history_path_)
                    #shutil.copy2(t_sou_file_list[s], t_des_abc_path)
                    #------------------------骁颖-----------------------
                    
                    t_message  = u"Success:拷贝成功:%s----->%s\n"%(unicode(t_sou_file_list[s]),unicode(t_des_abc_path))

                    __call_add_log(a_work_log_signal, a_work_log_function,t_message)
                except Exception,e:

                    t_message  = u"Error:拷贝失败:%s----->%s\n"%(unicode(t_sou_file_list[s]),unicode(t_des_abc_path))
                    a_fail_str = __call_copy_fail(a_fail_str, u"拷贝失败", unicode(t_sou_file_list[s]), unicode(t_des_abc_path))
                    __call_add_log(a_work_log_signal, a_work_log_function,t_message)
            else:

                if not os.path.exists( os.path.dirname(t_des_abc_path) ):
                    os.makedirs( os.path.dirname(t_des_abc_path) )
                try:
                    #------------------------骁颖-----------------------
                    
                    #===============骁颖==2018.06.15=========================
                    #shutil.copyfile(t_sou_file_list[s], t_des_abc_path)
                    ct.file().copy_file(t_sou_file_list[s], t_des_abc_path)
                    #try:
                        #shutil.copystat(t_sou_file_list[s], t_des_abc_path)
                    #except :
                        #pass
                    #===============骁颖==2018.06.15=========================
                        

                    #shutil.copy2(t_sou_file_list[s], t_des_abc_path)
                    #------------------------骁颖-----------------------
                    
                    
                    t_message  = u"Success:拷贝成功:%s----->%s\n"%(unicode(t_sou_file_list[s]),unicode(t_des_abc_path))
                    __call_add_log(a_work_log_signal, a_work_log_function,t_message)
                except Exception,e:

                    t_message  = u"Error:拷贝失败:%s----->%s\n"%(unicode(t_sou_file_list[s]),unicode(t_des_abc_path))
                    a_fail_str = __call_copy_fail(a_fail_str, u"拷贝失败", unicode(t_sou_file_list[s]), unicode(t_des_abc_path) )
                    __call_add_log(a_work_log_signal, a_work_log_function,t_message)
    if a_fail_str==False:
        return True
    else:
        return a_fail_str

    
    
