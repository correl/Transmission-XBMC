# -*- coding: utf-8 -*-

import os
import xbmc
import xbmcgui

__scriptname__ = "Transmission"
__author__ = "Correl"
__url__ = ""
__svn_url__ = ""
__credits__ = ""
__version__ = "0.5a"
__XBMC_Revision__ = "22240"

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

__language__ = xbmc.Language(os.getcwd()).getLocalizedString

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

if __name__ == '__main__':
    from gui import TransmissionGUI
    w = TransmissionGUI("script-Transmission-main.xml",os.getcwd() ,"default")
    w.doModal()
    del w
