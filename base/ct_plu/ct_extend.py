# -*- coding: utf-8 -*-
import os
import sys

from ct_data import ct_data
class ct_extend(object):
    def __init__(self):
        pass
    #a_data可以为任意类型的变量
    def ct_false(self, a_data=""):
        return ct_data().error(a_data)
    
    #a_data可以为任意类型的变量
    def ct_true(self, a_data=""):
        return ct_data().msg(a_data)
    
    #停止后续的插件/或者动作
    def ct_stop_next(self, a_data=""):
        return ct_data().stop_next(a_data)
        
    def run(self):
        pass


    

