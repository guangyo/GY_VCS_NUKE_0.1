import nuke,os,re,nukescripts
from src import getData,scriptCheck,withCgtw

''''
main module of VCS 
'''
def main():
    '''
    The main Function of VCS
    :return:
    '''
    p = VcsPanel()
    p.setMinimumSize(350,50)
    p.showModalDialog()


# User Panel
class VcsPanel(nukescripts.PythonPanel):
    def __init__(self):
        '''
        List all task of infomation
        '''
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

        #CREATE KNOBS
        self.projKnob = nuke.Enumeration_Knob('project','Proj/Eps/Shot/Version',[i[5:] for i in getData.get_pro_list(self.jsData)])
        self.epsKnob = nuke.Enumeration_Knob('eps','',[])
        self.shotKnob = nuke.Enumeration_Knob('shot','',[])
        self.verKnob = nuke.Enumeration_Knob('ver','',[])
        self.epsKnob.clearFlag(nuke.STARTLINE)
        self.shotKnob.clearFlag(nuke.STARTLINE)
        self.verKnob.clearFlag(nuke.STARTLINE)

        # CREATE BUTTON
        self.openFileButton = nuke.PyScript_Knob('openFile','Open File','')
        self.createFirstVersionButton = nuke.PyScript_Knob('cFirVer','Create First Version','')
        self.mergeMainVersionButton = nuke.PyScript_Knob('mMainVer','Merge Main Version','')
        self.upSubVersionButton = nuke.PyScript_Knob('upSubVer','Up Sub Version', '')
        self.upMainVersionButton = nuke.PyScript_Knob('upMainVer','Up Main Version','')
        # Set Flag
        self.openFileButton.setFlag(nuke.STARTLINE)
        self.createFirstVersionButton.setFlag(nuke.STARTLINE)
        self.upSubVersionButton.setFlag(nuke.STARTLINE)
        self.mergeMainVersionButton.setFlag(nuke.STARTLINE)

        # Set Visible
        self.hideAllButton()

        # ADD KNOBS
        for k in (self.projKnob, self.epsKnob, self.shotKnob, self.verKnob,self.createFirstVersionButton,self.upMainVersionButton,
                  self.upSubVersionButton,self.mergeMainVersionButton,self.openFileButton):
            self.addKnob(k)

    @staticmethod
    def have_this_task(file_path, dir_dict, ver_check):
        '''
        This function is make sure of have this task
        :param file_path:current nukeScript file path
        :param dir_dict:Project dir dict from json file
        :param ver_check:version check re funcion
        :return: str if current file is in or not in tasks
        if current file is untitled return 'untitle'
        '''

        if file_path == 'unsaveFile':
            return 'untitle'
        else:
            dir_name = os.path.dirname(file_path).replace('/','\\')
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
        '''
        This function is use to get info from current nuke file name
        :param filepath: base name of current nuke file
        :return: list of task information sorted with: [proj,eps,shot]
        '''

        return filepath.split('_')[:3]


    def knobChanged(self, knob):
        if knob is self.projKnob or knob.name() == 'showPanel':
            self.refresh_panel_with_project('proj_'+self.projKnob.value())
            self.refresh_version_panel(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account)
            self.version_check(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account,
                               self.verKnob.value())

        if knob is self.epsKnob:
            self.shotKnob.setValues(getData.get_shot_list(self.jsData,'proj_'+self.projKnob.value(),self.epsKnob.value()))
            self.refresh_version_panel(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account)

        if knob is self.shotKnob:
            self.refresh_version_panel(self.projKnob.value(),self.epsKnob.value(),self.shotKnob.value(),self.account)

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
            self.refresh_version_panel(self.projKnob.value(),self.epsKnob.value(),self.shotKnob.value(),self.account)
            self.verKnob.setValue(self.vernum_check.findall(self.current_file_path)[0])
            self.version_check(self.projKnob.value(),self.epsKnob.value(),self.shotKnob.value(),self.account,
                               self.verKnob.value())


        if knob is self.verKnob or knob is self.shotKnob or knob is self.epsKnob:
            self.version_check(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(), self.account,
                               self.verKnob.value())

        if knob is self.openFileButton:
            nuke.scriptOpen(self.get_filePath_from_knob())
            self.hide()

        if knob is self.mergeMainVersionButton:
            self.next_mainVersion(self.current_file_path)
            self.hide()

        if knob is self.upSubVersionButton:
            self.next_subVersion(self.current_file_path)
            self.hide()

        if knob is self.createFirstVersionButton:
            first_version_path = self.get_filePath_from_knob()
            nuke.scriptSaveAs(first_version_path)
            temp_file_match = re.compile(r'^%s_%s_%s_cmp_yourName_v\d{3,6}.nk$' %
                                         (self.projKnob.value(),self.epsKnob.value(),self.shotKnob.value()))
            ver_dict = getData.script_version_info(self.projKnob.value(),self.epsKnob.value(),
                                                   self.shotKnob.value(),self.account)
            if ver_dict['nukeScriptList']:
                # when have script already in this direction
                for script in ver_dict['nukeScriptList']:
                    # when have template file
                    if temp_file_match.match(script):
                        try:
                            nuke.scriptReadFile(os.path.dirname(first_version_path) + '/' + script)
                        except RuntimeError:
                            pass
                        for node in nuke.allNodes():
                            if node.Class() == 'Write':
                                temp_file_name = node['file'].getValue()
                                node['file'].setValue(temp_file_name.replace('yourName',self.account))
                        nuke.scriptSave()
            self.hide()

        if knob is self.upMainVersionButton:
            self.next_mainVersion(self.current_file_path)
            self.hide()


    def next_subVersion(self,path):
        """
        This function is use to Up subVersion
        :param path: path of current file
        :return: None
        """
        sub_version = 0
        verNum = self.vernum_check.findall(path)
        if len(verNum[-1]) == 4:
            # when current file is a main version
            # find last subVersion in this main version
            temp_sub_version_list = []
            verdict = getData.script_version_info(self.projKnob.value(), self.epsKnob.value(), self.shotKnob.value(),
                                                  self.account)['ver_dict']
            # take subVersion with this mainVersion in temp_sub_version_list
            for ver in verdict.keys():
                if verNum[-1] in ver and verdict[ver][1] == 'sub':
                    temp_sub_version_list.append(ver)

            if temp_sub_version_list:
                # if have subversion for in this main version
                sub_version = str(int(temp_sub_version_list[-1][-3:])+1).zfill(3)
            else:
                sub_version = '001'

            new_version_num = verNum[-1] + sub_version
            new_path = path.replace(verNum[-1], new_version_num)
            nuke.scriptSaveAs(new_path)
        else:
            # when current file is a sub version
            nukescripts.script_version_up()


    def next_mainVersion(self,path):
        """
        This function is use to Up mainVersion file
        :param path: path of current file
        :return: None
        """
        verNum = self.vernum_check.findall(path)
        if len(verNum[-1]) == 4:
            # when current file is a main version
            nukescripts.script_version_up()
        else:
            # when current file is a sub version
            new_version_num = verNum[-1][:4]
            new_path = path.replace(verNum[-1], new_version_num)
            nuke.scriptSaveAs(new_path)

            # set write export to publish
            cur_fileName = nuke.scriptName()
            publish_export_dir = os.path.dirname(cur_fileName)[:-4] + 'publish' + '/' + verNum[-1][:4]
            if not os.path.exists(publish_export_dir):
                os.makedirs(publish_export_dir)
            file_name = os.path.basename(cur_fileName).replace('.nk', '.mov')
            for node in nuke.allNodes():
                if node['name'].getValue() == 'Write_exr':
                    node['name'].setValue('Publish')
                    node['file'].setValue(publish_export_dir + '/' + file_name)
                    node['file_type'].setValue('mov')
                    return
            else:
                nuke.message('Not find Write node named Write_exr,please set the Write node by yourself~')





    def refresh_panel_with_project(self,proj):
        '''
        This function is use to refresh when project panel refresh
        :param proj:Value of project panel
        :return:None
        '''
        eps_list = getData.get_eps_list(self.jsData, proj)
        if eps_list:
            self.epsKnob.setValues(eps_list)
            self.epsKnob.setValue(str(eps_list[0]))
        shot_list = getData.get_shot_list(self.jsData,proj, self.epsKnob.value())
        if shot_list:
            self.shotKnob.setValues(shot_list)
            self.shotKnob.setValue(str(shot_list[0]))

    def refresh_version_panel(self,proj,eps,shot,account):
        '''
        This function is use to refresh version Panel
        :param proj:Project Name of user choose
        :param eps: eps Name of user choose
        :param shot: shot Name of user choose
        :param account: account Name of user choose
        :return: None
        '''
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


    def hideAllButton(self):
        '''
        Hide all button
        :return: None
        '''
        for b in (self.upMainVersionButton,self.openFileButton,self.createFirstVersionButton,self.upSubVersionButton,self.mergeMainVersionButton):
            b.setVisible(False)

    def version_check(self,proj,eps,shot,account,ver = 'v001'):
        '''
        This function is check version to set Knob
        :param proj:Project Name of user choose
        :param eps: eps Name of user choose
        :param shot: shot Name of user choose
        :param account: account Name of user choose
        :param ver: version of user choose
        :return: None
        '''
        self.ver_dict = getData.script_version_info(proj, eps, shot, account)
        if self.in_task != 'have':
            # when selected file is untitle or not in task
            if self.ver_dict['ver_dict'].keys():
                # when dir have version file
                self.hideAllButton()
                self.openFileButton.setVisible(True)
            else:
                # when dir is not have version file
                self.hideAllButton()
                self.createFirstVersionButton.setVisible(True)
        else:
            # when selected file in task
            try:
                if self.ver_dict['ver_dict'].keys() and self.ver_dict['ver_dict'][ver]:
                    # when dir have version file

                    # replace \\ to /
                    sel_fileName = self.ver_dict['ver_dict'][ver][0]
                    if '\\' in sel_fileName:
                        sel_fileName = sel_fileName.replace('\\', '/')

                    if sel_fileName == nuke.scriptName():
                        # when selected current file
                        if self.ver_dict['ver_dict'][ver][1] == 'main':
                            # when selected main version
                            if getData.get_status(self.jsData,'proj_'+self.projKnob.value(),self.epsKnob.value(),
                                                  self.shotKnob.value())[1] not in ['Publish','Wait']:
                                # when client not Publish or Wait
                                self.hideAllButton()
                                self.upMainVersionButton.setVisible(True)
                                self.upSubVersionButton.setVisible(True)
                                self.upSubVersionButton.clearFlag(nuke.STARTLINE)
                            else:
                                # when client need Publish
                                self.hideAllButton()
                                self.upSubVersionButton.setVisible(True)
                                self.upSubVersionButton.clearFlag(nuke.STARTLINE)
                        else:
                            # when selected sub version
                            self.hideAllButton()
                            self.upSubVersionButton.setVisible(True)
                            self.mergeMainVersionButton.setVisible(True)
                            self.mergeMainVersionButton.clearFlag(nuke.STARTLINE)
                    else:
                        # when selected other file
                        self.hideAllButton()
                        self.openFileButton.setVisible(True)
                else:
                    # when dir is not have version file
                    self.hideAllButton()
                    self.createFirstVersionButton.setVisible(True)
            except KeyError:
                self.hideAllButton()
                self.refresh_version_panel(self.projKnob.value(),self.epsKnob.value(),self.shotKnob.value(),self.account)


    def get_filePath_from_knob(self):
        '''
        Create File path from Knob value
        :return: string with File path
        '''

        if self.verKnob.visible():
            ver = self.verKnob.value()
        else:
            ver = '001001'

        filePath = 'Z:/GY_Project/{proj}/shot_work/{eps}/{shot}/cmp/work/{proj}_{eps}_{shot}_cmp_{account}_v{version}.nk'.format(
            proj = self.projKnob.value() , eps = self.epsKnob.value() , shot = self.shotKnob.value() , account = self.account,
            version = ver)
        return filePath



if __name__ == '__main__':
    main()





