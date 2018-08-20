import json,sys,os

sys.path.append(r"C:\cgteamwork\bin\base")
import cgtw

t_tw = cgtw.tw()

'''
This module is use to get all usefule data from CGTW 
'''

def getShotDatasToJSFile(path):
    '''
    This function is use to get shot data from CGTW with a json file
    :param path directory for json file path
    :return: None
    '''
    # get ready for get shot data ~_~
    shotDataList = []

    # get all projects in a list
    all_projects = getProjects()

    # get current user account
    account = t_tw.sys().get_account()

    for pro in all_projects:
        project_data_dict = {}
        # filter shots with project name
        filter_module = t_tw.task_module(pro, 'shot')

        # get eps shot and pipeline data from this project
        project_data_dict[pro] = filter_module.get_with_filter(['shot.shot', 'eps.eps_name', 'task.pipeline'],
                                              [['task.account', '=', account]])

        if len(project_data_dict[pro]) != 0:
            # Add data to shotDataList
            shotDataList.append(project_data_dict)

    #Save data to Json file
    jsShotDataList = json.dumps(shotDataList)
    with open(os.path.join(path,account+'.json'),'w') as f:
        f.write(jsShotDataList)

def getProjects():
    '''
    THis function is use to get all projects from CGTW
    :return: list for all projects name
    '''
    # great empty list use to get projectName
    project_final_list = []

    # get Project list from CGTW which project is not Lost and Close
    project_list = t_tw.info_module('public','project').\
        get_with_filter(['project.database'],
                        [['project.status','!=','Lost'],
                         'and',['project.status','!=','Close']])

    # get final list
    for pro in project_list:
        project_final_list.append(pro['project.database'])

    return project_final_list

if __name__ == '__main__':
    getShotDatasToJSFile(r'..\data')