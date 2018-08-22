import json,sys,os

'''
This module is use to get all useful data from CGTW 
'''

def getShotDatasToJSFile(path=r'C:\HOME\.nuke\VCS\DATA'):
    '''
    This function is use to get shot data from CGTW with a json file
    :param path directory for json file path
    :return: None
    '''
    # connect cgtw
    sys.path.append(r"C:\cgteamwork\bin\base")
    import cgtw
    t_tw = cgtw.tw()

    # get current user account
    account = t_tw.sys().get_account()

    # get ready for get shot data ~_~
    shotDataList = [account]

    # get all projects in a list
    all_projects = getProjects(t_tw)

    #Make sure of file path
    if not os.path.exists(path):
        os.makedirs(path)
    filepath = os.path.join(path,'data.json')

    for pro in all_projects:
        project_data_dict = {}
        # filter shots with project name
        filter_module = t_tw.task_module(pro, 'shot')

        # get eps shot and pipeline data from this project
        project_data_dict[pro] = filter_module.get_with_filter(['shot.shot', 'eps.eps_name', 'task.pipeline',
                                                                'task.leader_status','task.client_status'],
                                                                [['task.account', '=', account]])

        if len(project_data_dict[pro]) != 0:
            # Add data to shotDataList
            shotDataList.append(project_data_dict)

    #Save data to Json file
    jsShotDataList = json.dumps(shotDataList)
    with open(filepath,'w') as f:
        f.write(jsShotDataList)

def getProjects(t_tw):
    '''
    THis function is use to get all projects from CGTW
    :param t_tw:Class of CGTW object
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
    getShotDatasToJSFile()