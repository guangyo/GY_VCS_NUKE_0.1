import nuke
import os
import re
import nukescripts
from src import getData, scriptCheck, withCgtw

''''
main module of VCS 
'''


def main():
    """
    The main Function of VCS
    :return:
    """
    p = VcsPanel()
    p.setMinimumSize(350, 50)
    p.showModalDialog()


# User Panel
class VcsPanel(nukescripts.PythonPanel):
    def __init__(self):
        """
        List all task of infomation
        """
        # set Panel name
        nukescripts.PythonPanel.__init__(self, 'VCS0.1')

        # Write jsonData to Json file
        withCgtw.getShotDatasToJSFile()

        # get Data from json file
        self.jsData = getData.getJsonData()
        self.account = self.jsData[0]

        # get all task file paths
        self.proj_dir_dict = getData.getProjDirDict(self.jsData)

        # creat vertion re match
        self.ver_check = re.compile(r'^\d{3,6}.nk$', re.IGNORECASE)
        self.vernum_check = re.compile(r'v\d{3,6}', re.IGNORECASE)
        # use to match main version
        self.ver_main_check = re.compile(r'^\d\d\d.nk$', re.IGNORECASE)

        # use to match sub veision
        self.ver_sub_check = re.compile(r'^\d\d\d\d\d\d.nk$', re.IGNORECASE)

        # get current file path
        self.current_file_path = scriptCheck.get_current_script_name()

        # check current file if it in tasks
        self.in_task = self.have_this_task(self.current_file_path, self.proj_dir_dict, self.ver_check)

        # task info from current script file
        self.cur_task_info = []

        # if current file is not untitle save it for safe~
        if self.in_task != 'untitle':
            nuke.scriptSave()

        #  which direcion of user choose task
        self.choose_dir = ''

        # hide 'OK' and 'Cancle' button for default
        self.okButton = nuke.PyScript_Knob('none')

        # set default ver_dict
        self.ver_dict = {}

        # CREATE KNOBS
        self.projKnob = nuke.Enumeration_Knob('project', 'Proj/Eps/Shot/Version', [i[5:] for i in
                                                                                   getData.get_pro_list(self.jsData)])
        self.epsKnob = nuke.Enumeration_Knob('eps', '', [])
        self.shotKnob = nuke.Enumeration_Knob('shot', '', [])
        self.verKnob = nuke.Enumeration_Knob('ver', '', [])
        self.epsKnob.clearFlag(nuke.STARTLINE)
        self.shotKnob.clearFlag(nuke.STARTLINE)
        self.verKnob.clearFlag(nuke.STARTLINE)

        # CREATE BUTTON
        self.openFileButton = nuke.PyScript_Knob('openFile', 'Open File', '')
        self.createFirstVersionButton = nuke.PyScript_Knob('cFirVer', 'Create First Version', '')
        self.createMainVersionButton = nuke.PyScript_Knob('CMainVer', 'Create Main Version', '')
        self.upSubVersionButton = nuke.PyScript_Knob('upSubVer', 'Up Sub Version', '')
        self.upMainVersionButton = nuke.PyScript_Knob('upMainVer', 'Up Main Version', '')
        # Set Flag
        self.openFileButton.setFlag(nuke.STARTLINE)
        self.createFirstVersionButton.setFlag(nuke.STARTLINE)
        self.upSubVersionButton.setFlag(nuke.STARTLINE)
        self.createMainVersionButton.setFlag(nuke.STARTLINE)

        # Set Visible
        self.hideallbutton()

        # ADD KNOBS
        for k in (self.projKnob, self.epsKnob, self.shotKnob, self.verKnob, self.createFirstVersionButton,
                  self.upMainVersionButton, self.upSubVersionButton, self.createMainVersionButton, self.openFileButton):
            self.addKnob(k)

    @staticmethod
    def have_this_task(file_path, dir_dict, ver_check):
        """
        This function is make sure of have this task
        :param file_path:current nukeScript file path
        :param dir_dict:Project dir dict from json file
        :param ver_check:version check re funcion
        :return: str if current file is in or not in tasks
        if current file is untitled return 'untitle'
        """

        if file_path == 'unsaveFile':
            return 'untitle'
        else:
            dir_name = os.path.dirname(file_path).replace('/', '\\')
            if dir_name in dir_dict.keys():
                base_name = os.path.basename(file_path)
                template_file = dir_dict[dir_name]
                if template_file in base_name:
                    if ver_check.match(base_name.replace(template_file, '')):
                        return 'have'
                    else:
                        return 're Check Failed'
                else:
                    return 'template file not find'
            else:
                return 'not in dirs'

    @staticmethod
    def get_task_info_from_file(filepath):
        """
        This function is use to get info from current nuke file name
        :param filepath: base name of current nuke file
        :return: list of task information sorted with: [proj,eps,shot]
        """

        return filepath.split('_')[:3]

    def knobChanged(self, knob):
        if knob is self.projKnob or knob.name() == 'showPanel':
            self.refresh_panel_with_project('proj_'+self.projKnob.value())
            self.refresh_version_panel(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account)
            self.version_check(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account,
                               self.verKnob.value())

        if knob is self.epsKnob:
            self.shotKnob.setValues(getData.get_shot_list(self.jsData, 'proj_'+self.projKnob.value(),
                                                          self.epsKnob.value()))
            self.refresh_version_panel(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account)

        if knob is self.shotKnob:
            self.refresh_version_panel(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account)

        if knob.name() == 'showPanel' and self.in_task == 'have':
            '''
            Set default value with current task if this script in task
            '''
            # get task info from fileName
            self.cur_task_info = self.get_task_info_from_file(os.path.basename(self.current_file_path))
            # set Project Value
            self.projKnob.setValue(self.cur_task_info[0])
            # refresh Panel
            self.refresh_panel_with_project('proj_'+self.projKnob.value())
            # set default Panels
            self.epsKnob.setValue(self.cur_task_info[1])
            self.shotKnob.setValue(self.cur_task_info[2])
            self.refresh_version_panel(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account)
            self.verKnob.setValue(self.vernum_check.findall(self.current_file_path)[0])
            self.version_check(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account,
                               self.verKnob.value())

        if knob is self.verKnob or knob is self.shotKnob or knob is self.epsKnob:
            self.version_check(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account,
                               self.verKnob.value())

        if knob is self.openFileButton:
            nuke.scriptOpen(self.get_filepath_from_knob())
            self.hide()

        if knob is self.createMainVersionButton:
            self.next_mainversion(self.current_file_path)
            self.hide()

        if knob is self.upSubVersionButton:
            self.next_subversion(self.current_file_path)
            self.hide()

        if knob is self.createFirstVersionButton:
            first_version_path = self.get_filepath_from_knob()
            nuke.scriptSaveAs(first_version_path)
            temp_file_match = re.compile(r'^%s_%s_%s_cmp_yourName_v\d{3,6}.nk$' %
                                         (self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value()))
            ver_dict = getData.script_version_info(self.projKnob.value(), self.epsKnob.value(),
                                                   self.shotKnob.value(), self.account)
            if ver_dict['nukeScriptList']:
                # when have script already in this direction
                for script in ver_dict['nukeScriptList']:
                    # when have template file
                    if temp_file_match.match(script):
                        try:
                            nuke.scriptReadFile(os.path.dirname(first_version_path) + '/' + script)
                        except RuntimeError:
                            pass
                        for node in nuke.allNodes(filter='Write'):
                            if node.Class() == 'Write':
                                temp_file_name = node['file'].getValue()
                                node['file'].setValue(temp_file_name.replace('yourName', self.account))
                        nuke.scriptSave()
            self.hide()

        if knob is self.upMainVersionButton:
            self.next_mainversion(self.current_file_path)
            self.hide()

    def next_subversion(self, path):
        """
        This function is use to Up subVersion
        :param path: path of current file
        :return: None
        """
        vernum = self.vernum_check.findall(path)
        if len(vernum[-1]) == 4:
            # when current file is a main version
            # find last subVersion in this main version

            sub_version = 'v' + str(int(vernum[-1][1:]) + 1).zfill(3) + '001'
            new_version_num = sub_version
            new_path = path.replace(vernum[-1], new_version_num)
            nuke.scriptSaveAs(new_path)

            # set write export to subVersion
            cur_filename = nuke.scriptName()
            publish_export_dir = os.path.dirname(cur_filename)
            if not os.path.exists(publish_export_dir):
                os.makedirs(publish_export_dir)
            file_name = os.path.basename(cur_filename).replace('.nk', '.####.exr')
            for node in nuke.allNodes(filter='Write'):
                if node['name'].getValue() == 'Publish':
                    node['name'].setValue('Write_exr')
                    node['file'].setValue(publish_export_dir + '/render/' + new_version_num + '/' + file_name)
                    node['file_type'].setValue('exr')
                    return
                else:
                    nuke.message('Not find Write node named Write_exr,please set the Write node by yourself~')
        else:
            # when current file is a sub version
            nukescripts.script_version_up()

    def next_mainversion(self, path):
        """
        This function is use to Up mainVersion file
        :param path: path of current file
        :return: None
        """
        vernum = self.vernum_check.findall(path)

        new_version_num = vernum[-1][:4]
        new_path = path.replace(vernum[-1], new_version_num)
        nuke.scriptSaveAs(new_path)

        # set write export to publish
        cur_filename = nuke.scriptName()
        publish_export_dir = os.path.dirname(cur_filename)[:-4] + 'publish' + '/' + vernum[-1][:4]
        if not os.path.exists(publish_export_dir):
            os.makedirs(publish_export_dir)
        file_name = os.path.basename(cur_filename).replace('.nk', '.mov')
        for node in nuke.allNodes(filter='Write'):
            if node['name'].getValue() == 'Write_exr':
                node['name'].setValue('Publish')
                node['file'].setValue(publish_export_dir + '/' + file_name)
                node['file_type'].setValue('mov')
                return
            else:
                nuke.message('Not find Write node named Write_exr,please set the Write node by yourself~')

    def refresh_panel_with_project(self, proj):
        """
        This function is use to refresh when project panel refresh
        :param proj:Value of project panel
        :return:None
        """
        eps_list = getData.get_eps_list(self.jsData, proj)
        if eps_list:
            self.epsKnob.setValues(eps_list)
            self.epsKnob.setValue(str(eps_list[0]))
        shot_list = getData.get_shot_list(self.jsData, proj, self.epsKnob.value())
        if shot_list:
            self.shotKnob.setValues(shot_list)
            self.shotKnob.setValue(str(shot_list[0]))

    def refresh_version_panel(self, proj, eps, shot, account):
        """
        This function is use to refresh version Panel
        :param proj:Project Name of user choose
        :param eps: eps Name of user choose
        :param shot: shot Name of user choose
        :param account: account Name of user choose
        :return: None
        """
        try:
            self.ver_dict = getData.script_version_info(proj, eps, shot, account)
            if self.ver_dict['ver_dict'].keys():
                self.verKnob.setVisible(True)
                self.verKnob.setValues(self.ver_dict['ver_dict'].keys())
                self.verKnob.setValue(self.ver_dict['ver_dict'].keys()[0])
            else:
                self.verKnob.setVisible(False)
        except WindowsError:
            nuke.message('This project is too old~')

    def hideallbutton(self):
        """
        Hide all button
        :return: None
        """
        for b in (self.upMainVersionButton, self.openFileButton, self.createFirstVersionButton, self.upSubVersionButton,
                  self.createMainVersionButton):
            b.setVisible(False)

    def version_check(self, proj, eps, shot, account, ver='v001'):
        """
        This function is check version to set Knob
        :param proj:Project Name of user choose
        :param eps: eps Name of user choose
        :param shot: shot Name of user choose
        :param account: account Name of user choose
        :param ver: version of user choose
        :return: None
        """
        self.ver_dict = getData.script_version_info(proj, eps, shot, account)
        if self.in_task != 'have':
            # when selected file is untitle or not in task
            if self.ver_dict['ver_dict'].keys():
                # when dir have version file
                self.hideallbutton()
                self.openFileButton.setVisible(True)
            else:
                # when dir is not have version file
                self.hideallbutton()
                self.createFirstVersionButton.setVisible(True)
        else:
            # when selected file in task
            try:
                if self.ver_dict['ver_dict'].keys() and self.ver_dict['ver_dict'][ver]:
                    # when dir have version file

                    # replace \\ to /
                    sel_filename = self.ver_dict['ver_dict'][ver][0]
                    if '\\' in sel_filename:
                        sel_filename = sel_filename.replace('\\', '/')

                    if sel_filename == nuke.scriptName():
                        task_statu = getData.get_status(self.jsData, 'proj_'+self.projKnob.value(),
                                                        self.epsKnob.value(), self.shotKnob.value())
                        # when selected current file
                        if self.ver_dict['ver_dict'][ver][1] == 'main':
                            # when selected main version
                            if task_statu[1] != 'Retake':
                                # when client not Publish or Wait
                                self.hideallbutton()
                                # self.upMainVersionButton.setVisible(True)
                                # self.upSubVersionButton.setVisible(True)
                                # self.upSubVersionButton.clearFlag(nuke.STARTLINE)
                            else:
                                # when client need Retake
                                self.hideallbutton()
                                self.upSubVersionButton.setVisible(True)
                                self.upSubVersionButton.clearFlag(nuke.STARTLINE)
                        else:
                            # when selected sub version
                            if task_statu[0] == 'Publish':
                                # when leader statu is 'Publish'
                                self.hideallbutton()
                                self.upSubVersionButton.setVisible(True)
                                self.createMainVersionButton.setVisible(True)
                                self.createMainVersionButton.clearFlag(nuke.STARTLINE)
                            else:
                                # when leader statu is not 'Publish'
                                self.hideallbutton()
                                self.upSubVersionButton.setVisible(True)
                    else:
                        # when selected other file
                        self.hideallbutton()
                        self.openFileButton.setVisible(True)
                else:
                    # when dir is not have version file
                    self.hideallbutton()
                    self.createFirstVersionButton.setVisible(True)
            except KeyError:
                self.hideallbutton()
                self.refresh_version_panel(self.projKnob.value(), self.epsKnob.value(),
                                           self.shotKnob.value(), self.account)

    def get_filepath_from_knob(self):
        """
        Create File path from Knob value
        :return: string with File path
        """

        if self.verKnob.visible():
            ver = self.verKnob.value()
        else:
            ver = 'v001001'

        filepath = 'Z:/GY_Project/{proj}/shot_work/{eps}/{shot}/cmp/work/{proj}_{eps}_{shot}_cmp_{account}_{version}' \
                   '.nk'.format(proj=self.projKnob.value(), eps=self.epsKnob.value(), shot=self.shotKnob.value(),
                                account=self.account, version=ver)
        return filepath



