# coding: utf-8
import os,sys,json
from _lib import _lib
class _field:
    
    @staticmethod
    def create(a_fun, a_db, a_module, a_module_type, a_chinese_name, a_english_name, a_sign, a_type, a_field_name=""):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_chinese_name, (str, unicode)) or not isinstance(a_field_name, (str, unicode)) or not isinstance(a_sign, (str, unicode)) or\
           not isinstance(a_type, (str, unicode)) or not isinstance(a_field_name, (str, unicode)):
            raise Exception("_field.create argv error,  must be( str,str,str,str,str,str,str,str)")
        #t_type_list=_field.type().keys()
        t_type_list=_field.type()
        if a_type not in t_type_list:
            raise Exception("_field.create,  a_type in ( "+", ".join(t_type_list)+")")
        
        if a_sign.find(".")!=-1:
            raise Exception("_field.create,  a_sign error ,can not has '.' ")
        
        #if a_field_name.find(".")!=-1:
            #raise Exception("module.get_id ,  a_field_name error ,can not has '.' ")
        
        t_field_name=a_field_name
        if unicode(a_field_name).strip()=="":
            t_field_name=a_sign
        
        t_module=a_module
        if unicode(a_module_type).strip()=="task":
            t_module="task"
        
        return a_fun("c_field","python_create", {"db":a_db, "module": t_module, "field_str":a_chinese_name, "en_name":a_english_name, "sign":a_sign, "type":a_type, "field_name":t_field_name})	           
    
    @staticmethod
    def type():
        #t_type={
        #"int": u"整数",
        #"decimal": u"小数",
        #"lineedit": u"单行文本",
        #"textedit": u"多行文本",
        #"checkbox": u"单选框",
        #"list": u"列表"
        #}
        return ["int", "decimal", "lineedit", "textedit", "checkbox", "list"]