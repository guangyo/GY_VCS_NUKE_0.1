import sys,os,json,re
from collections import OrderedDict

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
    task_list = []
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

def script_version_info(proj,eps,shot,account):
    '''
    This function is use to check Version info of current task
    :param proj: proj name get from user Panel
    :param eps: eps name get from user Panel
    :param shot: shot name get from user Panel
    :return: Dict contains all info with this task version
    '''

    # create version re match
    ver_check = re.compile('^%s_%s_%s_cmp_%s_v\d\d\d_?\d{,3}.nk$' % (proj,eps,shot,account), re.IGNORECASE)
    vernum_check = re.compile(r'v\d\d\d_?\d{,3}', re.IGNORECASE)

    # use to match main version
    ver_main_check = re.compile(r'^\d\d\d.nk$', re.IGNORECASE)

    # use to match sub veision
    ver_sub_check = re.compile(r'^\d\d\d_\d{,3}.nk$', re.IGNORECASE)

    version_info = {}

    # all math version in this dict key is version number value is fileName for thisversion
    version_info['ver_dict'] = OrderedDict()

    dir_name = os.path.join('Z:/GY_Project',proj,'shot_work',eps,shot,'cmp','work')

    # List all .nk file in this task's dir
    version_info['nukeScriptList'] = [file for file in os.listdir(dir_name) if os.path.splitext(file)[1] == '.nk']

    # check versions which match format and create ver_dict
    for file in version_info['nukeScriptList']:
        if ver_check.match(file):
            ver_number = vernum_check.findall(file)[0]
            ver_number_len = len(ver_number)
            if ver_number_len == 4:
                version_status = 'main'
            elif ver_number_len > 4:
                version_status = 'sub'
            version_info['ver_dict'][ver_number] = [os.path.join(dir_name,file),version_status]
    return version_info

if __name__ == '__main__':
    print script_version_info('lah','01','shot02','billy')






