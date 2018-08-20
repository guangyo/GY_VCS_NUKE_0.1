import sys,os
sys.path.append(r"C:\cgteamwork\bin\base")
import cgtw


t_tw = cgtw.tw()
t_account = t_tw.sys().get_account()

t_filter_module = t_tw.task_module('proj_'+u'lah','shot')

print t_filter_module.get_with_filter(['shot.shot','eps.eps_name','task.pipeline'],[['task.account','=',t_account]])







