import os
import nuke

'''
This module contains functions with NukeScriptName check
'''

def get_current_script_name():
    '''
    This function is use to get current nuke fileName
    :return: str of current nuke script name if unsave will return
    'unsaveFile'
    '''
    try:
        return nuke.scriptName()
    except:
        return 'unsaveFile'

def get_last_Version():
    '''

    :return:
    '''
