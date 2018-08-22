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
        self.ver_check = re.compile(r'^\d\d\d_?\d{,3}$', re.IGNORECASE)

        # use to match main version
        self.ver_main_check = re.compile(r'^\d\d\d$', re.IGNORECASE)

        # use to match sub veision
        self.ver_sub_check = re.compile(r'^\d\d\d_\d{,3}$', re.IGNORECASE)

        # get current file path
        self.current_file_path = scriptCheck.get_current_script_name()

        # check current file if it in tasks
        self.in_task = self.have_this_task(self.current_file_path, self.proj_dir_dict, self.ver_check)

        # if current file is not untitle save it for safe~
        if self.in_task != 'untitle':
            nuke.scriptSave()

        nuke.message(self.in_task)

        #CREATE KNOBS
        self.projKnob = nuke.Enumeration_Knob('project','Proj',getData.get_pro_list(self.jsData))
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
        This function is make sure of have this
        :param file_path:current nukeScript file path
        :param dir_dict:Project dir dict from json file
        :param ver_check:version check re funcion
        :return: Bool if current file is in or not in tasks
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
            self.epsKnob.setValues(getData.get_eps_list(self.jsData,self.projKnob.value()))
            self.shotKnob.setValues(getData.get_shot_list(self.jsData, self.projKnob.value(), self.epsKnob.value()))
        if knob is self.epsKnob:
            self.shotKnob.setValues(getData.get_shot_list(self.jsData,self.projKnob.value(),self.epsKnob.value()))
        if self.in_task == 'have':
            self.cur_task_info = self.get_task_info_from_file(os.path.basename(self.current_file_path))
            self.projKnob.setValue('proj_'+self.cur_task_info[0])
            self.epsKnob.setValue(self.cur_task_info[1])
            self.shotKnob.setValue(self.cur_task_info[2])


# test:
if __name__ == '__main__':
    main()





