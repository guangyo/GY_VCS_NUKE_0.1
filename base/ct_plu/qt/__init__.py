import sys,os
ct_pyside = os.path.dirname(os.path.dirname(os.path.dirname(__file__.replace("\\","/"))))+"/lib/pyside"
if not ct_pyside in sys.path:
    sys.path.append(ct_pyside)

from PySide2.QtWidgets import *
from PySide2.QtWebSockets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtNetwork import *
from PySide2.QtWebEngineWidgets import *
from PySide2.QtWebEngineCore import *
from PySide2.QtWebChannel import *

from PySide2.QtXml import *
from PySide2.QtPrintSupport import *
from PySide2.QtMultimedia import *
from PySide2.QtMultimediaWidgets import *

