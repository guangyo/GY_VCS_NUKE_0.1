# coding: utf-8
import os,sys,json
from _lib import _lib
class _api_data:
    
    @staticmethod
    def set(a_fun, a_db, a_key, a_value, a_is_user=True):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_key, (str, unicode))  or not isinstance(a_value, (str, unicode))  or not isinstance(a_is_user, bool) :
            raise Exception("_api_data.set argv error,  must be( str,str,str,bool)")
        t_method="set_common"
        if a_is_user==True:
            t_method="set_user"
        return a_fun("c_api_data", t_method, {"db":a_db, "key":a_key, "value":a_value})
    
    @staticmethod
    def get(a_fun, a_db, a_key, a_is_user=True):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_key, (str, unicode))  or not isinstance(a_is_user, bool) :
            raise Exception("module.types argv error,  must be( str,str,bool)")
        t_method="get_common"
        if a_is_user==True:
                t_method="get_user"        
        return a_fun("c_api_data", t_method, {"db":a_db, "key":a_key})
