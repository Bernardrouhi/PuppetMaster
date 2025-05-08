from typing import List, Optional, Dict, Literal
import json
import os
import ntpath
from PuppetMaster.Core.PySideLibrary.QtWidgets import *
from PuppetMaster.Core.PySideLibrary.QtCore import *
from PuppetMaster.Core.PySideLibrary.QtGui import *

from PuppetMaster.Core.qnodes import PickNode, IMAGE_FORMATS
from PuppetMaster.Core.mayaHelper import mayaNamespace, getActiveItems
from PuppetMaster.Core.env_handler import is_PMWorkDir, get_PMTemplateDir, get_PMWorkDir
from PuppetMaster.UI.NamespaceDialog import NamespaceDialog
from PuppetMaster.UI.CreateTemplateDialog import TemplateDialog
from PuppetMaster.UI.QCanvas import CanvasGraphicsView


class CanvasGraphicsViewTab(QTabWidget):
    onSelection = Signal(PickNode)
    requestEditMode = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.editMode = False
        self.layout = QVBoxLayout(self)
        self.graphs:List[CanvasGraphicsView] = []
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)

    def get_node(self) -> Optional[CanvasGraphicsView]:
        """
        Get the current tab node.
        """
        index = self.currentIndex()
        if index >= 0:
            return self.graphs[index]
        return None

    def get_edit(self) -> bool:
        """
        Set the edit mode
        """
        return self.editMode

    def set_edit(self, value: bool) -> None:
        """
        Set the edit mode

        Parameters
        ----------
        value: (bool)
            Set the Edit mode.
        """
        self.editMode = value
        for each in self.graphs:
            each.Edit = self.editMode

    Edit = property(get_edit, set_edit)

    def get_data(self) -> dict:
        node = self.get_node()
        if node:
            return node.Raw
        return {}

    def set_data(self, value: dict) -> None:
        node = self.get_node()
        if node:
            node.Raw = value

    PII = property(get_data, set_data)

    def get_path(self) -> str:
        node = self.get_node()
        if node:
            return node.Path
        return ""

    def set_path(self, path: str) -> None:
        node = self.get_node()
        if node:
            node.Path = path

    Path = property(get_path, set_path)

    def get_name(self) -> str:
        index = self.currentIndex()
        if index >= 0:
            return self.tabText(index)
        return ""

    def set_name(self, text: str) -> None:
        index = self.currentIndex()
        if index >= 0:
            self.setTabText(index, text)

    Name = property(get_name, set_name)

    def new_tab(self) -> None:
        """
        Create a new tab.

        Return
        ------
        out: (CanvasGraphicsView)
            Get the canvas.
        """
        check = TemplateDialog()
        if check.exec_() == QDialog.Accepted:
            data = check.Raw
            name = data["name"] if data["name"] else "Untitled"
            self.load_tab(name=name, data=data['data'])

    def load_tab(self, name: str, data: dict) -> CanvasGraphicsView:
        newT = CanvasGraphicsView()
        newT.Edit = self.editMode
        newT.Raw = data

        newT.requestEditMode.connect(self.send_editMode_signal)
        newT.onSelection.connect(self.send_selection_signal)
        self.graphs.append(newT)
        self.addTab(newT, name)
        self.setCurrentIndex(self.graphs.index(newT))
        return newT

    def send_selection_signal(self, data: PickNode) -> None:
        self.onSelection.emit(data)

    def send_editMode_signal(self, value: bool) -> None:
        self.requestEditMode.emit(value)

    def set_background(self) -> None:
        """
        Set the background image.
        """
        node = self.get_node()
        if node:
            filePath, _ = QFileDialog.getOpenFileName(self, "Choose Background", "", "Image Files (*.png *.jpeg *.jpg)")
            if filePath.lower().endswith(IMAGE_FORMATS):
                node.BackgroundImage = filePath

    def set_namespace(self) -> None:
        """
        Change and set the new namespace.
        """
        node = self.get_node()
        if node:
            piiNames = node.Namespace
            validNames = list(set(mayaNamespace() + piiNames))
            self.newSpace = NamespaceDialog(namespaceList=piiNames, validList=validNames)
            if self.newSpace.exec_() == QDialog.Accepted:
                node.Namespace = self.newSpace.Raw

    def update_bg_color(self, color: QColor) -> None:
        """
        Set background color of selected nodes.

        Parameters
        ----------
        color: (QColor)
            QColor value.
        """
        node = self.get_node()
        if node:
            node.set_nodes_bg_color(color)

    def update_font_color(self, color: QColor) -> None:
        """
        Set font color of selected nodes.

        Parameters
        ----------
        color: (QColor)
            QColor value.
        """
        node = self.get_node()
        if node:
            node.set_nodes_font_color(color)

    def update_font_size(self, size: int) -> None:
        """
        Set font size of selected nodes.

        Parameters
        ----------
        size: (int)
            font size.
        """
        node = self.get_node()
        if node:
            node.set_nodes_font_size(size)

    def update_text(self, text: str) -> None:
        """
        Set text for selected nodes.

        Parameters
        ----------
        text: (str)
            text for the node.
        """
        node = self.get_node()
        if node:
            node.set_nodes_text(text)

    def update_shape(self, shape: str) -> None:
        """
        Set text for selected nodes.

        Parameters
        ----------
        text: (str)
            text for the node.
        """
        node = self.get_node()
        if node:
            node.set_nodes_shape(shape)

    def clear_content(self) -> None:
        """
        Clear Tab existing CanvasGraphicsView
        """
        node = self.get_node()
        if node:
            if node.is_changed():
                buttonReply = QMessageBox.warning(self, 'Clearing Tab', "Save the tab?",
                                                  QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
                if buttonReply == QMessageBox.Yes:
                    self.save_set()
                node.clear_scene()

    def open_set(self) -> None:
        """
        Create a new tab and open the .PII file.
        """
        work_dir = ""
        # Project Path
        if is_PMWorkDir():
            work_dir = get_PMWorkDir()
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
        # ask for location
        file_path, okPressed = QFileDialog.getOpenFileName(self, 'Open Picker Interface Information', work_dir,
                                                           "Picker Interface Information (*.pii)")
        if file_path:
            self.load_set(file_path)

    def refresh_set(self) -> None:
        """
        Refresh the current tab.
        """
        currentNode = self.get_node()
        if currentNode:
            path = currentNode.get_path()
            if os.path.exists(path):
                namespaceHistory = currentNode.NamespaceHistory
                currentNode.clear_scene()
                with open(path, 'r') as outfile:
                    self.set_data(json.load(outfile))
                piiNames = currentNode.Namespace
                piiNames.sort()
                if piiNames and namespaceHistory:
                    self.set_name(namespaceHistory)
                    currentNode.Namespace = {piiNames[0]: namespaceHistory}

    def force_load(self, paths: List[str]) -> None:
        """
        Load list of .PII files

        Parameters
        ----------
        paths: (list)
            List of .PII file.
        """
        for path in paths:
            if os.path.isfile(path):
                path = os.path.expandvars(path)
                self.load_set(path)

    def findAndLoad(self, names: List[Dict[Literal["name", "namespace"],str]]) -> None:
        """
        Find the names in the work folder and load them

        :param names: List of dictionaries of name and namespace.
        """
        template_dir = get_PMWorkDir()
        files = os.walk(template_dir).next()[2]
        for each in names:
            name = each['name']
            namespace = each['namespace']

            # valid files
            name_list = []
            for each in files:
                if name in each:
                    name_list.append(each)

            if name_list:
                name_list.sort()
                file_path = os.path.join(template_dir, name_list[-1])
                self.load_set(file_path)

                node = self.get_node()
                if node and namespace:
                    piiNames = node.Namespace
                    piiNames.sort()
                    node.Namespace = {piiNames[0]: namespace}
                    node.NamespaceHistory = namespace
                    # update tab name
                    piiNames = node.Namespace
                    piiNames.sort()
                    if piiNames:
                        self.set_name(piiNames[0].replace(':', ''))

    def load_set(self, path: str) -> None:
        """
        Load the .PII files

        Parameters
        ----------
        path: (str)
            Path of .PII file.
        """
        if path and path.lower().endswith(".pii"):
            with open(path, 'r') as outfile:
                self.load_tab(name=ntpath.basename(path), data=json.load(outfile))
                self.set_path(path)
                node = self.get_node()
                piiNames = node.Namespace
                piiNames.sort()
                if piiNames:
                    self.set_name(piiNames[0].replace(':', ''))

    def saveAs_set(self) -> None:
        """
        Save the Active tab as
        """
        node = self.get_node()
        if node:
            work_dir = get_PMWorkDir()
            scene_data = self.get_data()
            newPath, okPressed = QFileDialog.getSaveFileName(self, 'Save Tab', work_dir,
                                                             "Picker Interface Information (*.pii)")
            if newPath:
                # add extension
                if not newPath.lower().endswith('.pii'):
                    file_path = newPath + ".pii"
                else:
                    file_path = newPath

                self.set_path(file_path)
                with open(file_path, 'w') as outfile:
                    json.dump(scene_data, outfile, ensure_ascii=False, indent=4)

    def saveAsTemplate_set(self) -> None:
        """
        Save the Active tab as Template
        """
        node = self.get_node()
        if node:
            temp_dir = get_PMTemplateDir()
            scene_data = self.get_data()
            newPath, okPressed = QFileDialog.getSaveFileName(self, 'Save As Template', temp_dir,
                                                             "Picker Interface Information (*.pii)")
            if newPath:
                # add extension
                if not newPath.lower().endswith('.pii'):
                    file_path = newPath + ".pii"
                else:
                    file_path = newPath
                with open(file_path, 'w') as outfile:
                    json.dump(scene_data, outfile, ensure_ascii=False, indent=4)

    def rename_set(self) -> None:
        """
        Rename the active tab.
        """
        node = self.get_node()
        if node:
            text, okPressed = QInputDialog.getText(self, "Tab Name", "Name", QLineEdit.Normal, "")
            if okPressed and text:
                self.set_name(text)

    def closeTab(self, index: int) -> None:
        """
        Close the tab.

        Parameters
        ----------
        index: (int)
            Index of the tab.
        """
        name = self.tabText(index)
        message = 'Are you sure you want to close the tab "{}"?\n\nAll Changes will be lost.'.format(name)
        buttonReply = QMessageBox.warning(self, 'Close Tab', message, QMessageBox.Cancel | QMessageBox.Ok,
                                          QMessageBox.Ok)
        if buttonReply == QMessageBox.Ok:
            del self.graphs[index]
            self.removeTab(index)

    def closeCurrentTab(self) -> None:
        """
        Close the active tab.
        """
        index = self.currentIndex()
        if index >= 0:
            self.closeTab(index)

    def save_set(self) -> None:
        """
        Save the active tab
        """
        node = self.get_node()
        if node:
            file_path = self.get_path()
            # check for file path
            if file_path:
                scene_data = self.get_data()
                fileName = self.get_name()
                self.set_path(file_path)
                with open(file_path, 'w') as outfile:
                    json.dump(scene_data, outfile, ensure_ascii=False, indent=4)
            else:
                self.saveAs_set()

    def maya_selection(self, *args, **kwargs) -> None:
        selected = getActiveItems()
        node = self.get_node()
        if node:
            node.Highlight = selected
