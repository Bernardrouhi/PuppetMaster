from maya import cmds
from maya import mel
from maya import OpenMayaUI as omui
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QWidget, QMessageBox)
from shiboken2 import wrapInstance


def selectObjects(nodes=list):
    '''
    Select objects in maya.

    Parameters
    ----------
    nodes: (list)
        List of object's name.
    '''
    cmds.select(nodes, add=True)

def clearSelection():
    '''
    Clear Maya selection.
    '''
    cmds.select(clear=True)

def getActiveItems():
    return cmds.ls(selection=True, long=False)

def runMel(cmd=str):
    '''
    Run mel commands.

    Parameters
    ----------
    cmd: (str)
        Commands in Mel language.
    '''
    if cmd:
        mel.eval(cmd)

def mayaNamespace():
    '''
    Get list of Maya namespaces.

    Return
    ------
    out: (list)
        List of Maya namespaces.
    '''
    cmds.namespace(setNamespace=':')
    return cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)

def runPython(cmd=str):
    '''
    Run python commands.

    Parameters
    ----------
    cmd: (str)
        commands in Python language.
    '''
    if cmd:
        try:
            exec(cmd)
        except SyntaxError as err:
            dial = QMessageBox()
            dial.setText(str(err))
            dial.setWindowTitle("Caution!")
            dial.setIcon(QMessageBox.Warning)
            dial.addButton('Ok', QMessageBox.RejectRole)
            dial.exec_()
        except Exception as err:
            dial = QMessageBox()
            dial.setText(str(err))
            dial.setWindowTitle("Caution!")
            dial.setIcon(QMessageBox.Warning)
            dial.addButton('Ok', QMessageBox.RejectRole)
            dial.exec_()

def maya_version():
    '''
    Get current maya versions
    '''
    return cmds.about(version=True)

def warningMes(msg):
    '''
    Print out warning message.

    Parameters
    ----------
    msg: (str)
        message to show on console.
    '''
    cmds.warning(msg)

def errorMes(msg):
    '''
    Print out error message.

    Parameters
    ----------
    msg: (str)
        message to show on console.
    '''
    cmds.error(msg)

def get_MayaWindow():
    '''
    Get the maya window.
    '''
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    # graphEdtrPtr = omUI.MQtUtil.findLayout("graphEditor1Window|TearOffPane|graphEditor1")
    return wrapInstance(long(mayaMainWindowPtr), QWidget)
