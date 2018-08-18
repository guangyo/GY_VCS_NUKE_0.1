# coding: utf-8
import os,sys,json
class _link:
    
    @staticmethod
    def link_asset(a_fun, a_db, a_module, a_module_type, a_id_list, a_link_id_list):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list) or not isinstance(a_link_id_list, list) :
            raise Exception("_link.link_asset argv error,  must be( str,str,str,list, list)")
        if len(a_id_list)==0 or len(a_link_id_list)==0:
            return False
        return a_fun("c_many2many", "add_link", {"db":a_db, "module":a_module, "module_type":a_module_type, "module_tab_id_array":a_id_list, "link_module":"asset", "link_module_tab_id_array":a_link_id_list, "is_main":"Y"})
        
    @staticmethod
    def unlink_asset(a_fun, a_db, a_module, a_module_type, a_id_list, a_link_id_list):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id_list, list) or not isinstance(a_link_id_list, list) :
            raise Exception("_link.unlink_asset argv error,  must be( str,str,str,list, list)")
        if len(a_id_list)==0 or len(a_link_id_list)==0:
            return False
        return a_fun("c_many2many", "remove_link", {"db":a_db, "module":a_module, "module_type":a_module_type, "module_tab_id_array":a_id_list, "link_module":"asset", "link_module_tab_id_array":a_link_id_list, "is_main":"Y"})

    

    @staticmethod
    def get_asset(a_fun, a_db, a_module, a_module_type, a_id):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_module, (str, unicode)) or not isinstance(a_module_type, (str, unicode)) or \
           not isinstance(a_id, (str, unicode)) :
            raise Exception("_link.get_asset argv error,  must be( str,str,str,str)")
        return a_fun("c_many2many", "get_link", {"db":a_db, "module":a_module, "module_type":a_module_type, "module_tab_id":a_id, "link_module":"asset","is_main":"Y"})
        
