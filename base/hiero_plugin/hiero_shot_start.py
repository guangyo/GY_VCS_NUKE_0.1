#coding:utf8
import os,sys
G_base_path = unicode(os.path.dirname(os.path.dirname( sys.argv[0] ))).replace("\\","/")
G_Icon_path = G_base_path + u"/com_icon/"
if not G_base_path in sys.path:
    sys.path.append( G_base_path )
from cgtw import *


from hiero_shot_ui import Ui_Form
from PySide import QtCore,QtGui
from PySide.QtCore import *
from PySide.QtGui import *
my_pyside_windows=""
from hiero.core import *
from hiero.ui import *
from hiero_shot_plugin import * 
hiero.core.events.registerInterest("kShowContextMenu/kTimeline",create_shot_menu)
