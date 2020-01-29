#!/usr/bin/python

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QWidget, QHBoxLayout)

from widgets.CustomeWidget import PuppetMaster
from core.mayaHelper import get_MayaWindow

TITLE = "Puppet Master v1.0.0"

#Widget
class PMQWidget(QWidget):
    def __init__(self, parent=get_MayaWindow(), *args, **kwargs):
        super(PMQWidget, self).__init__(parent=parent, *args, **kwargs)
        self.setWindowTitle(TITLE)
        self.setObjectName('PuppetMaster')
        self.layout = QHBoxLayout(self)
        self.pm = PuppetMaster()
        self.layout.addWidget(self.pm)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(1280, 720)

    def destroyMayaSignals(self):
        '''
        Destroy the maya signal listener
        '''
        if self.pm:
            self.pm.destroyMayaSignals()

    def force_load(self, paths=list()):
        '''
        Load list of .PII files

        Parameters
        ----------
        paths: (list)
            List of .PII file.
        '''
        if paths:
            self.pm.force_load(paths)

    def findAndLoad(self, names=list()):
        '''
        Find the names in work folder and load them

        Parameters
        ----------
        names: (list)
            List of dictionaries of name and namespace.
        '''
        if names:
            self.pm.findAndLoad(names)

    def closeEvent(self, event):
        if self.pm:
            self.pm.destroyMayaSignals()
        event.accept()
