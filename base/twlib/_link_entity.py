# coding: utf-8
import os,sys,json
from _lib import _lib
class _link_entity:
    
    @staticmethod
    def get_name(a_fun, a_db, a_link_id):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_link_id, (str, unicode)):
            raise Exception("_link_entity.get_name argv error(str, str)")                        
        return a_fun("c_link_entity", "get_entity_name", {"db":a_db, "link_id":a_link_id})
    
    @staticmethod
    def get(a_fun, a_db, a_filter_list=[]):
        if isinstance(a_db, (str, unicode))==False or isinstance(a_filter_list, list)==False:
            raise Exception("_link_entity.get argv error(str, list)")                        
        return a_fun("c_link_entity", "get_with_filter", {"db":a_db, "filter_array":a_filter_list})
    
    @staticmethod
    def fields():
        #t_field={
        #"#id": u"id",
        #"#link_id": u"关联的任务的ID",
        #"module":"模块",
        #"module_type": u"模块类型",
        #}
        return ["#id", "#link_id", "module", "module_type"]    
    