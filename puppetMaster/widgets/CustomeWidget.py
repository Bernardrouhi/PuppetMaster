
import webbrowser
from PySide2.QtWidgets import (QMainWindow, QDockWidget, QWidget, QAction, 
                          QMenuBar)
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt, Signal
from ..core.qnodes import PickNode
from ..core.mayaHelper import warningMes
from CustomeTabWidget import CanvasGraphicsViewTab
from ParametersWidget import Parameters


import maya.OpenMaya as OpenMaya

class PuppetMaster(QMainWindow):
    requestEditMode = Signal(bool)
    def __init__(self, parent=None, editMode=bool(False)):
        super(PuppetMaster, self).__init__(parent)
        self._parent = parent
        self._model = list()
        self.editMode = editMode

        self.setMouseTracking(True)

        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowTitle('PuppetMaster')

        self.setMinimumHeight(1)
        self.setMinimumWidth(1)

        self.setContextMenuPolicy(Qt.PreventContextMenu)

        # Main tabs
        self.tab = CanvasGraphicsViewTab(parent=self)
        self.tab.requestEditMode.connect(self.set_edit)
        self.setCentralWidget(self.tab)

        # Parameter Widget
        self.parameter = Parameters(parent=self)

        self.parameterDock = QDockWidget(": Parameters ::", self)
        self.parameterDock.setObjectName('Parameters')
        self.parameterDock.setFeatures(QDockWidget.DockWidgetClosable)
        self.parameterDock.setWidget(self.parameter)
        self.parameterDock.setTitleBarWidget(QWidget(self.parameterDock))
        self.parameterDock.setVisible(self.editMode)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.parameterDock)

        self.tab.onSelection.connect(self.update_parameters)
        self.parameter.onChangeBGColor.connect(self.tab.update_bg_color)
        self.parameter.onChangeFontColor.connect(self.tab.update_font_color)
        self.parameter.onChangeFontSize.connect(self.tab.update_font_size)
        self.parameter.onChangeText.connect(self.tab.update_text)
        self.parameter.onChangeShape.connect(self.tab.update_shape)

        # maya Signal on selection items
        self.idx = OpenMaya.MEventMessage.addEventCallback("SelectionChanged", self.tab.maya_selection)

        # Menu
        self.setMenuBar(self.create_menu())

        self.set_edit(self.editMode)

    def update_parameters(self, node=PickNode):
        shape = node.Shape if isinstance(node, PickNode) else str()
        self.parameter.update_param(
            text=node.toPlainText(), 
            fontSize=node.font().pointSize(), 
            fontColor=node.defaultTextColor(), 
            bgColor=node.Background,
            shapeName=shape)

    def create_menu(self):
        window_menu = QMenuBar(self)
        file_menu = window_menu.addMenu("&File")

        new_action = QAction("&New...", self)
        new_action.setShortcut('Ctrl+N')
        new_action.setShortcutContext(Qt.WidgetShortcut)
        new_action.setStatusTip('Create a new Set')
        new_action.triggered.connect(self.tab.new_tab)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut('Ctrl+O')
        open_action.setShortcutContext(Qt.WidgetShortcut)
        open_action.setStatusTip('Open a new set')
        open_action.triggered.connect(self.tab.open_set)
        file_menu.addAction(open_action)

        refresh_action = QAction("&Refresh...", self)
        refresh_action.setStatusTip('Refresh the current sets')
        refresh_action.triggered.connect(self.tab.refresh_set)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        save_action = QAction("&Save...", self)
        save_action.setShortcut('Ctrl+S')
        save_action.setShortcutContext(Qt.WidgetShortcut)
        save_action.setStatusTip('Save the current tab')
        save_action.triggered.connect(self.tab.save_set)
        file_menu.addAction(save_action)

        saveAs_action = QAction("&Save As...", self)
        saveAs_action.setShortcut('Ctrl+Shift+S')
        saveAs_action.setShortcutContext(Qt.WidgetShortcut)
        saveAs_action.setStatusTip('Save the current tab as a new Set')
        saveAs_action.triggered.connect(self.tab.saveAs_set)
        file_menu.addAction(saveAs_action)

        saveAsTemp_action = QAction("&Save As Template...", self)
        saveAsTemp_action.setStatusTip('Save the current tab as a new Template')
        saveAsTemp_action.triggered.connect(self.tab.saveAsTemplate_set)
        file_menu.addAction(saveAsTemp_action)

        file_menu.addSeparator()

        rename_action = QAction("&Rename Tab...", self)
        rename_action.setStatusTip('Rename the current Tab')
        rename_action.triggered.connect(self.tab.rename_set)
        file_menu.addAction(rename_action)

        close_action = QAction("&Close Tab...", self)
        close_action.setShortcut('Ctrl+Shift+W')
        close_action.setShortcutContext(Qt.WidgetShortcut)
        close_action.setStatusTip('Close the current Tab')
        close_action.triggered.connect(self.tab.closeCurrentTab)
        file_menu.addAction(close_action)

        picker_menu = window_menu.addMenu("&Picker")

        self.edit_action = QAction("&Edit Mode", self)
        self.edit_action.setStatusTip('Toggle between view and edit mode.')
        self.edit_action.triggered.connect(self.edit_toggle)
        self.edit_action.setCheckable(True)
        self.edit_action.setChecked(self.editMode)
        picker_menu.addAction(self.edit_action)

        picker_menu.addSeparator()

        self.background_action = QAction("&Change Background...", self)
        self.background_action.setEnabled(self.editMode)
        self.background_action.setStatusTip('Change the background.')
        self.background_action.triggered.connect(self.tab.set_background)
        picker_menu.addAction(self.background_action)

        self.namespace_action = QAction("&Change Namespace...", self)
        self.namespace_action.setEnabled(self.editMode)
        self.namespace_action.setStatusTip('Change the namespace.')
        self.namespace_action.triggered.connect(self.tab.set_namespace)
        picker_menu.addAction(self.namespace_action)

        help_menu = window_menu.addMenu("&Help")

        wiki_action = QAction("&About PuppetMaster...", self)
        wiki_action.setStatusTip('Open Wiki page')
        wiki_action.triggered.connect(self.wiki_open)
        help_menu.addAction(wiki_action)

        return window_menu

    def edit_toggle(self):
        self.set_edit(not self.editMode)

    def wiki_open(self):
        webbrowser.open_new_tab('https://github.com/Bernardrouhi/PuppetMaster/wiki')

    def force_load(self, paths=list):
        self.tab.force_load(paths)

    def findAndLoad(self, names=list()):
        '''
        Find the names in PuppetMaster folder and load them

        Parameters
        ----------
        names: (list)
            List of dictionaries of name and namespace.
        '''
        if names:
            self.tab.findAndLoad(names)

    def destroyMayaSignals(self):
        # destroy the connection
        OpenMaya.MMessage.removeCallback(self.idx)

    def get_edit(self):
        return self.editMode
    def set_edit(self, value=bool):
        self.editMode = value
        self.background_action.setEnabled(self.editMode)
        self.namespace_action.setEnabled(self.editMode)
        self.parameterDock.setVisible(self.editMode)
        self.edit_action.setChecked(self.editMode)
        self.tab.Edit = self.editMode 
        # Notification
        if not self.editMode:
            warningMes("PUPPETMASTER-INFO: Out of 'Edit Mode' you won't be able to create/edit/move or delete any node.")
        else:
            warningMes("PUPPETMASTER-INFO: In 'Edit Mode' command buttons won't run any commands.")
    Edit = property(get_edit,set_edit)

    def keyPressEvent(self, event):
        if event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            if event.key() == Qt.Key_W:
                self.tab.closeCurrentTab()
            elif event.key() == Qt.Key_S:
                self.tab.saveAs_set()
        elif event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_S:
                    self.tab.save_set()
            elif event.key() == Qt.Key_N:
                self.tab.new_tab()
            elif event.key() == Qt.Key_O:
                self.tab.open_set()
        else:
            super(PuppetMaster, self).keyPressEvent(event)
