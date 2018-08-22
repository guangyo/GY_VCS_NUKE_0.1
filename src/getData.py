import sys,os,json

# direction of JSON file
jsonFilePath = r'C:\HOME\.nuke\VCS\DATA\data.json'

'''
This module is use to get and filter Data from Json file
'''
# get Data from json file
def getJsonData():
    '''
    This function is use to get data from json file
    :return:
    '''
    with open(jsonFilePath, 'r') as f:
        jsFileData = f.read()
    return json.loads(jsFileData)

# get account
def get_account(data):
    '''
    This funcion is use to get account
    :param data: list data from json file
    :return: string user account
    '''
    return data[0]

def get_pro_list(data):
    '''
    This funcion is use to get project list
    :param data: list data from json file
    :return: list of all projects
    '''
    project_list = []
    for pro in data[1:]:
        for key in pro.keys():
            if 'proj_' in key:
                project_list.append(key)

    return project_list

def get_eps_list(data,project):
    '''
    This function is use to get eps list when user choose project
    :param data: list data from json file
    :param project: project with use choose
    :return: list with eps list
    '''

    eps_list = []

    task_list = get_task_list(data,project)

    for task in task_list:
        eps_list.append(task['eps.eps_name'])

    # remove repeat eps name
    eps_list = list(set(eps_list))
    return eps_list

def get_task_list(data,proj):
    '''
    This funcion is use to get Task list from json data
    :param data: list data from json file
    :param proj: project name with user choose
    :return: list of all task in this project
    '''
    for project in data[1:]:
        if proj in project.keys():
            task_list = project[proj]
    return task_list

def get_shot_list(data,proj,eps):
    '''
    This Funcion is use to get shot list
    :param data: list data from json file
    :param proj: project with use choose
    :param eps: eps_name from use choose
    :return: list with all shots in this eps
    '''

    shot_list = []

    task_list = get_task_list(data,proj)

    for task in task_list:
        if eps == task['eps.eps_name']:
            shot_list.append(task['shot.shot'])

    return shot_list

def get_status(data,proj,eps,shot):
    '''
    This function is use to get status of current shot
    :param data: list data from json file
    :param proj: project with use choose
    :param eps: eps_name from use choose
    :param shot: shot from user selected
    :return: list status of current shot first one is leader_status
    second one is client_status
    '''
    status_list = []

    task_list = get_task_list(data, proj)

    for task in task_list:
        if eps == task['eps.eps_name'] and shot == task['shot.shot']:
            status_list.extend([task['task.leader_status'],task['task.client_status']])

    return status_list

def getProjDirDict(data):
    '''
    This funcion is use to get all project direcion list
    :data: Json data from json file
    :return:dict of all project directionList with task this user have,
    key is path of task project dir
    value is projectFilename template
    '''

    projDirDict = {}

    for pro in data[1:]:
        for task in pro.values()[0]:
            file_path = os.path.join(r'Z:\GY_Project',pro.keys()[0][5:],'shot_work',
                                     task['eps.eps_name'],task['shot.shot'],
                                     task['task.pipeline'],'work')

            projDirDict[file_path] = pro.keys()[0][5:]+'_'+task['eps.eps_name']+'_'+task['shot.shot']+'_'+task['task.pipeline']+'_'+data[0]+'_'+'v'

    return projDirDict

if __name__ == '__main__':
    print getProjDirDict(getJsonData())






