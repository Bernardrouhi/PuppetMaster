import os
from typing import Optional, List
from PySideWrapper.QtCore import *
from PySideWrapper.QtWidgets import *
from PySideWrapper.QtGui import *

from maya import OpenMaya

from PuppetMaster.UI.CustomeWidget import PuppetMaster

TITLE = "Puppet Master v1.0.1"


class PMQWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.setWindowTitle(TITLE)
        self.setObjectName('PuppetMaster')
        self.layout = QHBoxLayout(self)
        self.pm = PuppetMaster()
        self.layout.addWidget(self.pm)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(1280, 720)

    def force_load(self, paths: List[str]) -> None:
        """
        Load list of PII files
        :param paths: list of a path to .PII files
        """
        if paths:
            self.pm.force_load(paths)

    def findAndLoad(self, names: List[str]) -> None:
        """
        Find the names in the work folder and load them
        """
        if names:
            self.pm.findAndLoad(names)


class PuppetMasterMainWindow(QMainWindow):
    onSelectionChanged = Signal()
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self._signals = []
        version = os.getenv("PUPPET_MASTER_VERSION")
        self.setWindowTitle(f"Puppet Master {version}")
        self.setObjectName('PuppetMaster')
        self.addSignals()
        self._init_ui()
        self.resize(1280, 720)

    def _init_ui(self) -> None:
        widget = PuppetMaster()
        self.setCentralWidget(widget)
        self.onSelectionChanged.connect(widget.callSelectionChanged)

    # ====================== Maya Signals ======================
    def _onSelectionChanged(self, arg: None) -> None:
        """ Signal of maya call when selection changed. """
        self.onSelectionChanged.emit()

    def addSignals(self) -> None:
        """ Bind Maya signals. """
        if self._signals: self.removeSignals()
        self._signals.append(
            OpenMaya.MEventMessage.addEventCallback("SelectionChanged", self._onSelectionChanged)
        )

    def removeSignals(self) -> None:
        """ Remove Maya signals. """
        if self._signals:
            for _ in self._signals: OpenMaya.MMessage.removeCallback(_)
        self._signals.clear()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.removeSignals()
