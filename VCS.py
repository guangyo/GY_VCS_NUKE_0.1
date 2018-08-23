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

        # get Data form json file
        self.jsData = getData.getJsonData()

        # get all task file paths
        self.proj_dir_dict = getData.getProjDirDict(self.jsData)

        # creat vertion re match
        self.ver_check = re.compile(r'^\d\d\d_?\d{,3}.nk$', re.IGNORECASE)

        # use to match main version
        self.ver_main_check = re.compile(r'^\d\d\d.nk$', re.IGNORECASE)

        # use to match sub veision
        self.ver_sub_check = re.compile(r'^\d\d\d_\d{,3}.nk$', re.IGNORECASE)

        # get current file path
        self.current_file_path = scriptCheck.get_current_script_name()

        # check current file if it in tasks
        self.in_task = self.have_this_task(self.current_file_path, self.proj_dir_dict, self.ver_check)

        # task info from current script file
        self.cur_task_info = []

        # if current file is not untitle save it for safe~
        if self.in_task != 'untitle':
            nuke.scriptSave()

        #CREATE KNOBS
        self.projKnob = nuke.Enumeration_Knob('project','Proj',[i[5:] for i in getData.get_pro_list(self.jsData)])
        self.epsKnob = nuke.Enumeration_Knob('eps','',[])
        self.shotKnob = nuke.Enumeration_Knob('shot','',[])
        self.epsKnob.clearFlag(nuke.STARTLINE)
        self.shotKnob.clearFlag(nuke.STARTLINE)
        # ADD KNOBS
        for k in (self.projKnob,self.epsKnob,self.shotKnob):
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

        return filepath.split('_')[:2]

    def knobChanged(self, knob):
        if knob is self.projKnob or knob.name() == 'showPanel':
            self.refresh_panel_with_project('proj_'+self.projKnob.value())

        if knob is self.epsKnob:
            self.shotKnob.setValues(getData.get_shot_list(self.jsData,'proj_'+self.projKnob.value(),self.epsKnob.value()))

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
            # set eps and shot Panel
            self.epsKnob.setValue(self.cur_task_info[1])
            self.shotKnob.setValue(self.cur_task_info[2])

    def refresh_panel_with_project(self,proj):
        '''
        This function is use to refresh when project panel refresh
        :param proj:Value of project panel
        :return:None
        '''
        self.epsKnob.setValues(getData.get_eps_list(self.jsData, proj))
        self.shotKnob.setValues(getData.get_shot_list(self.jsData,proj, self.epsKnob.value()))


# test:
if __name__ == '__main__':
    main()





