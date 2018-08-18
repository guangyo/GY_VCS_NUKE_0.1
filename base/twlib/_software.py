# coding: utf-8
import os,sys,json
from _lib import _lib
class _software:
    @staticmethod
    def get_path(a_fun, a_db, a_name):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_name, (str, unicode)) :
            raise Exception("_software.get_path argv error,  must be( str, str)")
        return a_fun("c_software", "get_software_path", {"db":a_db, "name":a_name})    
    
    @staticmethod
    def get_with_type(a_fun, a_db, a_type):
        if not isinstance(a_db, (str, unicode)) or not isinstance(a_type, (str, unicode)) :
            raise Exception("_software.get_with_type argv error,  must be( str, str)")
        return a_fun("c_software", "get_software_with_type", {"db":a_db, "type":a_type}) 


    @staticmethod
    def types(a_fun):
        return a_fun("c_software", "get_software_type", {})