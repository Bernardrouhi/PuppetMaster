from typing import List
from maya import cmds
from maya import mel
import pymel.core as pm
from PySideWrapper.QtWidgets import *


def selectObjects(nodes: List[str]) -> None:
    """
    Select objects in maya.
    :param nodes:List of object's name
    """
    pm.select(nodes, add=True)


def clearSelection() -> None:
    """ Clear Maya selection. """
    pm.select(clear=True)


def getActiveItems() -> List[str]:
    return cmds.ls(selection=True, long=False)


def runMel(cmd: str) -> None:
    """
    Run mel commands.
    :param cmd: Commands to run.
    """
    mel.eval(cmd)


def mayaNamespace() -> List[str]:
    """
    Get list of Maya namespaces.

    Return
    ------
    out: (list)
        List of Maya namespaces.
    """
    cmds.namespace(setNamespace=':')
    return cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)


def runPython(cmd: str) -> None:
    """
    Run python commands.

    Parameters
    ----------
    cmd: (str)
        commands in Python language.
    """
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


def maya_version() -> str:
    """ Get current maya versions. """
    return pm.about(version=True)


def warningMes(msg: str) -> None:
    """ Print out a warning message. """
    pm.warning(msg)


def errorMes(msg: str) -> None:
    """ Print out an error message. """
    pm.error(msg)


def mayaMainWindow() -> QMainWindow:
    return pm.ui.Window("MayaWindow").asQtObject()
