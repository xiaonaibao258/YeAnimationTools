import os,sys
import maya.cmds as cmds
import maya.mel as mel

def shelfButtonInstall():
    PATH = os.path.dirname(__file__) 
    PATH = os.path.abspath(PATH).replace('\\','/') 
    print(PATH)

    Label = "AT"
    Script = '''#
import sys
if "{0}" not in sys.path:
    sys.path.append("{0}")

import {1} as AT
import importlib
importlib.reload(AT)

AT_PATH = "{0}"
# 显示UI
if __name__ == "__main__":
    try:
        A.close()  # 如果有相同名称的窗口，则关闭
    except:
        pass
    A = AT.AnimationTools(AT_PATH)
    A.show()
'''.format(PATH, 'AnimationTools') 

    mel.eval('global string $gShelfTopLevel') 
    gShelfTopLevel = mel.eval('$tmp = $gShelfTopLevel') 

    currentShelf = cmds.tabLayout(gShelfTopLevel, query=True, selectTab=True)
    cmds.setParent(currentShelf)

    icon = PATH+'/AnimationTools.png'

    cmds.shelfButton( 
        command = Script,
        annotation = Label,
        label = Label,
        imageOverlayLabel = Label,
        image = icon,
        image1 = icon,
        sourceType = "python"
    ) 

def onMayaDroppedPythonFile(param):
    shelfButtonInstall()
