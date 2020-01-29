from PySide2.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                          QFrame, QMenu, QGraphicsItem, QDialog, QApplication)
from PySide2.QtCore import (Qt, QRectF, QBuffer, QIODevice, QByteArray,
                       QPoint, Signal, QMimeData, QPointF, QEvent)
from PySide2.QtGui import (QColor, QPixmap, QBrush, QPainter, QCursor, QFont, QMouseEvent)
from ..core.icon import iconSVG, QIconSVG

from ..core.qnodes import (IMAGE_FORMATS, PickNode, ButtonNode, PII, PIINode, PIIPick, 
                           PickShape, CommandType, PIIButton)
from ..core.mayaHelper import (selectObjects, getActiveItems, clearSelection,
                               runPython, runMel, errorMes)
from CommandDialog import CommandDialog

class CanvasGraphicsView(QGraphicsView):
    onSelection = Signal(PickNode)
    requestEditMode = Signal(bool)
    def __init__(self, parent=None):
        super(CanvasGraphicsView, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        # Scene properties
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(51, 51, 51)))
        self.setFrameShape(QFrame.NoFrame)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.ViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)

        self.init()

    def init(self):
        self.piiPath = str()
        self._model = {
            'background':str()
        }
        self._isPanning = False
        self._isZooming = False
        self._mousePressed = False
        self._scene = QGraphicsScene()
        self._scene.selectionChanged.connect(self.update_node_settings)
        self._backgroundNode = QGraphicsPixmapItem()
        self._scene.addItem(self._backgroundNode)
        self._orderSelected = list()
        self._lastPos = QPoint(0,0)
        self.editMode = False
        self._namespace = str()
        self._dragMulti = list()

        self._defaultColor = QColor(255,255,255)
        self._defaultTextColor = QColor(0,0,0)
        self._defaultTextSize = 20
        self._defaultText = "New Node"

        self.workHight = 2160
        self.workWidth = 4096

        self.setScene(self._scene)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setBackgroundImage(str())

    def update_node_settings(self):
        if self._orderSelected:
            node = self._orderSelected[-1]
            self._defaultText = node.toPlainText()
            self._defaultColor = node.Background
            self._defaultTextColor = node.defaultTextColor()
            self._defaultTextSize = node.font().pointSize()

    def update_maya_selection(self):
        '''
        Update Maya Scene base on active selection.
        '''
        clearSelection()
        selection = list()
        for each in self._orderSelected:
            selection += each.Items
        if selection:
            selectObjects(selection)

    def setBackgroundImage(self, path=str()):
        '''
        Set background image

        Parameters
        ----------
        path: (str)
            Path to background image.
        '''
        self._model['background'] = path
        self.setStatusTip(self._model['background'])
        pixmap = QPixmap(self._model['background'])
        self._backgroundNode.setPixmap(pixmap)
    def getBackgroundImage(self):
        '''
        Get background image
        '''
        return self._model['background']
    BackgroundImage = property(getBackgroundImage,setBackgroundImage)

    def actionMenu(self, QPos):
        '''
        Show action menu.

        Parameters
        ----------
        QPos: (list)
            list of x and y location.
        '''
        self.mainMenu = QMenu()

        add_action = self.mainMenu.addAction('Add A Button')
        add_action.setEnabled(self.editMode)
        add_action.triggered.connect(self.add_node)

        addMany_action = self.mainMenu.addAction('Add Many Buttons')
        addMany_action.setEnabled(self.editMode)
        addMany_action.triggered.connect(self.add_multiple_nodes)

        activeNode = self.mouse_on_node()
        if activeNode:
            update_action = self.mainMenu.addAction('Update Button')
            update_action.setEnabled(self.editMode)
            update_action.triggered.connect(lambda: self.update_node(activeNode))

        delete_action = self.mainMenu.addAction('Delete Button')
        delete_action.setEnabled(self.editMode)
        delete_action.setShortcut('Backspace')
        delete_action.triggered.connect(self.removeSelected)

        self.mainMenu.addSeparator()

        # search for selected ButtonNode
        btnStatus = [isinstance(n, ButtonNode) for n in self._scene.selectedItems()]
        if True in btnStatus:
            # first ButtonNode
            activeNode = self._scene.selectedItems()[btnStatus.index(True)]
            command_action = self.mainMenu.addAction('Edit Command Button...')
            command_action.setEnabled(self.editMode)
            command_action.triggered.connect(lambda: self.update_ButtonNode(activeNode))
        else:
            command_action = self.mainMenu.addAction('add Command Button...')
            command_action.setEnabled(self.editMode)
            command_action.triggered.connect(self.add_commands)

        self.mainMenu.addSeparator()

        reset_action = self.mainMenu.addAction('Reset View')
        reset_action.setShortcut('H')
        reset_action.triggered.connect(self.reset_view)

        frame_action = self.mainMenu.addAction('Frame View')
        frame_action.setShortcut('F')
        frame_action.triggered.connect(self.frame_view)

        self.mainMenu.addSeparator()

        alignGrp = QMenu('Align')
        self.mainMenu.addMenu(alignGrp)

        hac_action = alignGrp.addAction('Horizontal Align Center')
        hac_action.setIcon(QIconSVG('h_align-01'))
        hac_action.setEnabled(self.editMode)
        hac_action.triggered.connect(self.align_horizontal)

        vac_action = alignGrp.addAction('Vertical Align Center')
        vac_action.setIcon(QIconSVG('v_align-01'))
        vac_action.setEnabled(self.editMode)
        vac_action.triggered.connect(self.align_vertical)

        hd_action = alignGrp.addAction('Horizontal Distribute')
        hd_action.setIcon(QIconSVG('h_d_align-01'))
        hd_action.setEnabled(self.editMode)
        hd_action.triggered.connect(self.align_horizontal_distribute)

        vd_action = alignGrp.addAction('Vertical Distribute')
        vd_action.setIcon(QIconSVG('v_d_align-01'))
        vd_action.setEnabled(self.editMode)
        vd_action.triggered.connect(self.align_vertical_distribute)

        alignGrp.addSeparator()

        ins_action = alignGrp.addAction('Increase Size')
        ins_action.setShortcut('+')
        ins_action.setEnabled(self.editMode)
        ins_action.triggered.connect(self.increase_size)

        dis_action = alignGrp.addAction('Decrease Size')
        dis_action.setShortcut('-')
        dis_action.setEnabled(self.editMode)
        dis_action.triggered.connect(self.decrease_size)

        self.mainMenu.addSeparator()

        edit_mode = self.mainMenu.addAction('Edit Mode')
        edit_mode.setCheckable(True)
        edit_mode.setChecked(self.editMode)
        edit_mode.triggered.connect(lambda: self.request_edit(not self.editMode))

        pos = self.mapToGlobal(QPoint(0,0))
        self.mainMenu.move(pos + QPos)
        self.mainMenu.show()

    def mouse_on_node(self):
        globPosition = self.mapFromGlobal(QCursor.pos())
        scenePosition =  self.mapToScene(globPosition)
        for node in self._scene.items():
            if isinstance(node, PickNode):
                if node.mapRectToScene(node.boundingRect()).contains(scenePosition):
                    return node
        return None

    def update_node(self, node=PickNode):
        '''
        Update the Node selection base on selection in maya.
        '''
        mayaScene = getActiveItems()
        # for each in self._scene.selectedItems():
        node.Items = mayaScene

    def update_ButtonNode(self, node=ButtonNode):
        '''
        Update the ButtonNode commands.

        Parameters
        ----------
        node: (ButtonNode)
            ButtonNode Node.
        '''
        self.newCommand = CommandDialog(
            text = node.toPlainText(),
            cmd = node.Command,
            cmdType = node.CommandsType
        )
        if self.newCommand.exec_() == QDialog.Accepted:
            data = self.newCommand.Raw
            node.setPlainText(data[PIIButton.TEXT])
            node.Command = data[PIIButton.COMMAND]
            node.CommandsType = data[PIIButton.COMMANDTYPE]

    def add_commands(self):
        '''
        Create a new ButtonNode with Commands.
        '''
        globPosition = self.mapFromGlobal(QCursor.pos())
        scenePosition =  self.mapToScene(globPosition)
        self.newCommand = CommandDialog()
        if self.newCommand.exec_() == QDialog.Accepted:
            data = self.newCommand.Raw
            self.create_button(
                position = scenePosition, 
                text = data[PIIButton.TEXT], 
                size = self._defaultTextSize, 
                textColor = self._defaultTextColor, 
                bgColor = self._defaultColor,
                cmd = data[PIIButton.COMMAND], 
                cmdType = data[PIIButton.COMMANDTYPE])

    def align_horizontal(self):
        '''
        Align the selection to center horizontally.
        '''
        selected = self._scene.selectedItems()
        if len(selected) > 1:
            minValue = selected[0].y()
            maxValue = selected[0].y()
            whole = None
            for each in selected:
                y = each.y()
                value = y + each.boundingRect().height()
                # finding lowest value
                minValue = y if y < minValue else minValue
                minValue = value if value < minValue else minValue
                # finding highest value
                maxValue = y if y > maxValue else maxValue
                maxValue = value if value > maxValue else maxValue

            total = maxValue - minValue
            if total != 0:
                middle = (maxValue + minValue)/2
                for each in selected:
                    center = each.shape().boundingRect().center()
                    start_y = each.y()
                    offset = start_y + center.y() - middle
                    each.setY(each.y() - offset)
    def align_vertical(self):
        '''
        Align the selection to center vertically.
        '''
        selected = self._scene.selectedItems()
        if len(selected) > 1:
            # sort it based on x position + width
            selected = sorted(selected, key=lambda x:x.x()+x.boundingRect().width())
            leftNode = selected[0]
            rightNode = selected[-1]
            # total length of x axis
            total = rightNode.boundingRect().width() + rightNode.x() - leftNode.x()
            if total != 0:
                middle = (total/2) + leftNode.x()
                for each in selected:
                    center = each.shape().boundingRect().center()
                    start_x = each.x()
                    offset = start_x + center.x() - middle
                    each.setX(each.x() - offset)
    def align_horizontal_distribute(self):
        '''
        Disturbute the selected nodes evenly between first node on the left and last 
        node on the right horizontally.
        '''
        selected = self._scene.selectedItems()
        if len(selected) > 2:
            # sort it based on x position + width
            selected = sorted(selected, key=lambda x:x.x()+x.boundingRect().width())
            startItem = selected.pop(0)
            endItem = selected.pop(-1)

            # total length of items
            itemsLength = int()
            for each in selected:
                itemsLength += each.boundingRect().width()

            startPoint = startItem.x() + startItem.boundingRect().width()
            total = endItem.x() - startPoint
            section_num = len(selected) + 1
            extraSpace = total - itemsLength
            # nicly divide
            if extraSpace > 0:
                gap = extraSpace/section_num
                nextPlace = startPoint
                for each in selected:
                    newLoc = nextPlace + gap
                    nextPlace += gap + each.boundingRect().width()
                    each.setX(newLoc)
            else:
                total = endItem.x() - startPoint
                gap = total/section_num
                nextPlace = startPoint
                for each in selected:
                    nextPlace += gap
                    each.setX(nextPlace)
        else:
            errorMes("PUPPETMASTER-INFO: Select more than 2 nodes.")
    def align_vertical_distribute(self):
        '''
        Disturbute the selected nodes evenly between first node on the top and last 
        node on the bottom vertically.
        '''
        selected = self._scene.selectedItems()
        if len(selected) > 2:
            # sort it based on y position + width
            selected = sorted(selected, key=lambda node:node.y()+node.boundingRect().height())
            startItem = selected.pop(0)
            endItem = selected.pop(-1)

            # total length of items
            itemsLength = int()
            for each in selected:
                itemsLength += each.boundingRect().height()

            startPoint = startItem.y() + startItem.boundingRect().height()
            total = endItem.y() - startPoint
            section_num = len(selected) + 1
            extraSpace = total - itemsLength
            # nicly divide
            if extraSpace > 0:
                gap = extraSpace/section_num
                nextPlace = startPoint
                for each in selected:
                    newLoc = nextPlace + gap
                    nextPlace += gap + each.boundingRect().height()
                    each.setY(newLoc)
            else:
                total = endItem.y() - startPoint
                gap = total/section_num
                nextPlace = startPoint
                for each in selected:
                    nextPlace += gap
                    each.setY(nextPlace)
        else:
            errorMes("PUPPETMASTER-INFO: Select more than 2 nodes.")

    def reset_view(self):
        '''
        Fit all the items to the view.
        '''
        items = self._scene.items()
        if items:
            rects = [item.mapToScene(item.boundingRect()).boundingRect() for item in items]
            rect = self.min_bounding_rect(rects)
            self._scene.setSceneRect(rect)
            self.fitInView(rect, Qt.KeepAspectRatio)
    def frame_view(self):
        '''
        Fit selected items to the view.
        '''
        items = self._scene.selectedItems()
        if items:
            rects = [item.mapToScene(item.boundingRect()).boundingRect() for item in items]
            rect = self.min_bounding_rect(rects)
            self.fitInView(rect, Qt.KeepAspectRatio)

    def fit_contents(self):
        '''
        Update the scene boundery.
        '''
        items = self._scene.items()
        if items:
            rects = [item.mapToScene(item.boundingRect()).boundingRect() for item in items]
            rect = self.min_bounding_rect(rects)
            self._scene.setSceneRect(rect)

    def request_edit(self, value=bool):
        self.requestEditMode.emit(value)

    def min_bounding_rect(self, rectList=list()):
        '''
        Get the minimum boundry based on objects in the scene.

        Parameters
        ----------
        rectList: (list)
            List of QRectF (boundry of objects)

        Return
        ------
        out: (QRectF)
            Get the minimum boundry
        '''
        minX = rectList[0].left()
        minY = rectList[0].top()
        maxX = rectList[0].right()
        maxY = rectList[0].bottom()

        for k in range(1, len(rectList)):
            minX = min(minX, rectList[k].left())
            minY = min(minY, rectList[k].top())
            maxX = max(maxX, rectList[k].right())
            maxY = max(maxY, rectList[k].bottom())

        return QRectF(minX, minY, maxX-minX, maxY-minY)

    def increase_size(self):
        '''
        Increase the size of selected items by 1 unit.
        '''
        selected = self._scene.selectedItems()
        for each in selected:
            font = each.font()
            fontSize = font.pointSize()
            if fontSize < 99:
                fontSize += 1
                font.setPointSize(fontSize)
                each.setFont(font)

    def decrease_size(self):
        '''
        Decrease the size of selected items by 1 unit.
        '''
        selected = self._scene.selectedItems()
        for each in selected:
            font = each.font()
            fontSize = font.pointSize()
            if fontSize > 1:
                fontSize -= 1
                font.setPointSize(fontSize)
                each.setFont(font)

    def is_texture(self, path=str):
        '''
        Check if the texture path is valid.

        Return
        ------
        out: (bool)
            True if texture is valide, otherwise False.
        '''
        if path.lower().endswith(IMAGE_FORMATS):
            return True
        return False

    def _QMimeDataToFile(self, data=QMimeData):
        '''
        Get all the filepath from drag file.

        Parameters
        ----------
        data: (QMimeData)
            QMimeData of dragged file.
        '''
        files = list()
        if data.hasUrls:
            for each in data.urls():
                files.append(each.toLocalFile())
        return files
    def _is_dragValid(self, event):
        '''
        Check for draged file validation
        '''
        dragedItems = self._QMimeDataToFile(event.mimeData())
        if dragedItems:
            first_path = dragedItems[0]
            if self.is_texture(first_path) and self.editMode:
                return True
        return False
    def dragEnterEvent(self, event):
        event.accept() if self._is_dragValid(event) else event.ignore()
    def dragMoveEvent(self, event):
        event.accept() if self._is_dragValid(event) else event.ignore()
    def dropEvent(self, event):
        dragedItems = self._QMimeDataToFile(event.mimeData())
        if dragedItems:
            first_path = dragedItems[0]
            if self.is_texture(first_path):
                self.setBackgroundImage(path=first_path)
                event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        self._lastPos = event.pos()
        self._lastScenePos = self.mapToScene(event.pos())
        if self._dragMulti:
            for each in self._dragMulti:
                each.setSelected(True)
            self._dragMulti = list()
        if event.button() == Qt.MiddleButton:
            self._isPanning = True
            self.setCursor(QPixmap(iconSVG('nav-pan-02')))
            self._dragPos = event.pos()
            event.accept()
        elif event.button() == Qt.RightButton:
            if event.modifiers() == Qt.AltModifier:
                self._isZooming = True
                self.setCursor(QPixmap(iconSVG('nav-zoom-02')))
                self._dragPos = event.pos()
                self._dragPos2 = self.mapToScene(event.pos())
            else:
                self.actionMenu(event.pos())
            event.accept()
        else:
            super(CanvasGraphicsView, self).mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self._dragMulti and len(self._dragMulti) > 1:
            start =  self._lastScenePos
            end =  self.mapToScene(event.pos())

            total = len(self._dragMulti)-1
            xLength = start.x() - end.x()
            yLength = start.y() - end.y()
            xStep = 0 if xLength == 0 else -(xLength/total)
            yStep = 0 if yLength == 0 else -(yLength/total)
            num = 0
            for each in self._dragMulti:
                position = QPointF(start.x() + (num * xStep), start.y() + (num * yStep)) 
                each.setPos(position)
                num += 1

        if self._isPanning:
            newPos = event.pos()
            diff = newPos - self._dragPos
            self._dragPos = newPos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
            event.accept()
        elif self._isZooming:
            newPos = event.pos()
            diff = newPos - self._dragPos
            self._dragPos = newPos
            factor = 1.000
            if diff.x() < 0:
                factor = 0.98
            else:
                factor = 1.02

            self.scale(factor, factor)
            event.accept()
        else:
            if event.modifiers() == Qt.ShiftModifier:
                diff = event.pos() - self._lastPos
                x = event.x() if abs(diff.x()) > abs(diff.y()) else self._lastPos.x()
                y = event.y() if abs(diff.y()) > abs(diff.x()) else self._lastPos.y()
                event = QMouseEvent(QEvent.MouseMove, QPoint(x, y), self.mapToGlobal(QPoint(x, y)), Qt.LeftButton,Qt.LeftButton, Qt.NoModifier)
            super(CanvasGraphicsView, self).mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        self._isPanning = False
        self._isZooming = False
        self.setCursor(Qt.ArrowCursor)
        super(CanvasGraphicsView, self).mouseReleaseEvent(event)
        self.fit_contents()
        self.update_maya_selection()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
            if self.editMode:
                self.removeSelected()
        elif event.key() == Qt.Key_Plus:
            if self.editMode:
                self.increase_size()
        elif event.key() == Qt.Key_Minus:
            if self.editMode:
                self.decrease_size()
        elif event.key() == Qt.Key_H:
            self.reset_view()
        elif event.key() == Qt.Key_F:
            self.frame_view()
        else:
            super(CanvasGraphicsView, self).keyPressEvent(event)

    def removeSelected(self):
        '''
        Remove selected Items.
        '''
        for each in self._scene.selectedItems():
            self._scene.removeItem(each)
            self.remove_stack(each)

    def wheelEvent(self,  event):
        factor = 1.05
        if event.delta() < 0:
            # factor = .2 / factor
            factor = 0.95
        self.scale(factor, factor)
        self.update()

    def add_node(self):
        '''
        Add a new PickNode to the scene.
        '''
        # Cursor Position on Scene
        globPosition = self.mapFromGlobal(QCursor.pos())
        scenePosition =  self.mapToScene(globPosition)
        
        self.create_node(
            text = self._defaultText,
            size = self._defaultTextSize,
            textColor = self._defaultTextColor,
            bgColor = self._defaultColor,
            position = scenePosition,
            items = getActiveItems(),
            shape = PickShape.SQUARE
        )

    def add_multiple_nodes(self):
        '''
        Add group of PickNode bellow each other to the scene.
        '''
        # Cursor Position on Scene
        globPosition = self.mapFromGlobal(QCursor.pos())
        scenePosition =  self.mapToScene(globPosition)

        self._dragMulti = list()
        for each in getActiveItems():
            node = self.create_node(
                text = self._defaultText,
                size = self._defaultTextSize,
                textColor = self._defaultTextColor,
                bgColor = self._defaultColor,
                position = scenePosition,
                items = [each],
                shape = PickShape.SQUARE
            )
            self._dragMulti.append(node)
            # scenePosition = QPointF(scenePosition.x(), node.y() + node.boundingRect().height() + 5)

    def create_node(self, position=list, text=str, size=int, textColor=QColor, bgColor=QColor, items=list, shape=PickShape.SQUARE):
        '''
        Create a new PickNode.

        Parameters
        ----------
        position: (list)
            List of x and y location.
        text: (str)
            Name of the text.
        size: (int)
            Size of the text.
        textColor: (QColor)
            Color of the text.
        bgColor: (QColor)
            Background Color of the node.
        items: (list)
            List of selected Maya object.

        Return
        ------
        out: (PickNode)
            Reference of created Node.
        '''
        textNode = PickNode()
        font = QFont("SansSerif", size)
        font.setStyleHint(QFont.Helvetica)
        textNode.setFont(font)
        textNode.setDefaultTextColor(textColor)
        textNode.setFlag(QGraphicsItem.ItemIsMovable, self.editMode)
        textNode.setFlag(QGraphicsItem.ItemIsSelectable)
        # textNode.setFlag(QGraphicsItem.ItemIsFocusable, self.editMode)
        textNode.Background = bgColor
        textNode.Items = items
        textNode.Shape = shape

        textNode.onSelected.connect(lambda: self.onSelection.emit(textNode))
        textNode.onAddToStack.connect(lambda: self.add_stack(textNode))
        textNode.onRemoveFromStack.connect(lambda: self.remove_stack(textNode))

        textNode.setPos(position)
        textNode.setPlainText(text)

        self._scene.addItem(textNode)
        return textNode
    
    def create_button(self, position=list, text=str, size=int, textColor=QColor, bgColor=QColor, cmd=str, cmdType=str):
        '''
        Create a new ButtonNode.

        Parameters
        ----------
        position: (list)
            List of x and y location.
        text: (str)
            Name of the text.
        size: (int)
            Size of the text.
        textColor: (QColor)
            Color of the text.
        bgColor: (QColor)
            Background Color of the node.
        cmd: (str)
            Command to run when it's pressed.
        cmdType: (str)
            Type of command.("python"/"mel")
        '''
        btnNode = ButtonNode()
        font = QFont("SansSerif", size)
        font.setStyleHint(QFont.Helvetica)
        btnNode.setFont(font)
        btnNode.setDefaultTextColor(textColor)
        btnNode.setFlag(QGraphicsItem.ItemIsMovable, self.editMode)
        btnNode.setFlag(QGraphicsItem.ItemIsSelectable)
        btnNode.Background = bgColor
        btnNode.CommandsType = cmdType
        btnNode.Command = cmd

        # btnNode.onSelected.connect(lambda: self.onSelection.emit(textNode))
        btnNode.onSelected.connect(lambda: self.onSelection.emit(btnNode))
        btnNode.onClicked.connect(self.scriptJob)

        btnNode.setPos(position)
        btnNode.setPlainText(text)

        self._scene.addItem(btnNode)

    def scriptJob(self, cmdType=str, cmd=str):
        '''
        Run a command.

        Parameters
        ----------
        cmd: (str)
            Command to run.
        cmdType: (str)
            Type of command.("python"/"mel")
        '''
        if not self.editMode:
            if cmdType == CommandType.PYTHON:
                runPython(cmd)
            elif cmdType == CommandType.MEL:
                runMel(cmd)

    def add_stack(self, node=PickNode):
        '''
        Add a node selection in right order into the stack.

        Parameters
        ----------
        node: (PickNode)
            Selected node.
        '''
        self._orderSelected.append(node)
    def remove_stack(self, node=PickNode):
        '''
        Remove a node from the stack.

        Parameters
        ----------
        node: (PickNode)
            Selected node.
        '''
        if node in self._orderSelected:
            index = self._orderSelected.index(node)
            self._orderSelected.pop(index)

    def get_edit(self):
        return self.editMode
    def set_edit(self, value=bool):
        self.editMode = value
        for each in self._scene.items():
            if type(each) == PickNode:
                each.setFlag(QGraphicsItem.ItemIsMovable, self.editMode)
            elif type(each) == ButtonNode:
                each.setFlag(QGraphicsItem.ItemIsMovable, self.editMode)
    Edit = property(get_edit,set_edit)

    def get_path(self):
        return self.piiPath
    def set_path(self, path=str):
        self.piiPath = path
    Path = property(get_path, set_path)

    def get_raw(self):
        '''
        Get the scene information. (can be be save in .pii)

        Return
        ------
        out: (dict)
            Dictionary of scene date to be save in .pii file.
        '''
        image_data = str()
        pixmap = self._backgroundNode.pixmap()
        # Extract Image Data
        if not pixmap.isNull():
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, "PNG")
            # Image Data
            image_data = bytes(buffer.data().toBase64()).decode('ascii')

        nodeList = []
        for each in self._scene.items():
            if type(each) == PickNode:
                textColor = each.defaultTextColor()
                bgColor = each.Background
                item = {
                    PIIPick.TYPE:PIINode.PICK,
                    PIIPick.TEXT: each.toPlainText(),
                    PIIPick.SIZE: each.font().pointSize(),
                    PIIPick.POSITION: (each.pos().x(),each.pos().y()),
                    PIIPick.COLOR: (textColor.red(),textColor.green(),textColor.blue()),
                    PIIPick.BACKGROUND: (bgColor.red(),bgColor.green(),bgColor.blue()),
                    PIIPick.SELECTION: each.Items,
                    PIIPick.SHAPE: each.Shape
                }
                nodeList.append(item)
            elif type(each) == ButtonNode:
                textColor = each.defaultTextColor()
                bgColor = each.Background
                item = {
                    PIIButton.TYPE:PIINode.BUTTON,
                    PIIButton.TEXT: each.toPlainText(),
                    PIIButton.SIZE: each.font().pointSize(),
                    PIIButton.POSITION: (each.pos().x(),each.pos().y()),
                    PIIButton.COLOR: (textColor.red(),textColor.green(),textColor.blue()),
                    PIIButton.BACKGROUND: (bgColor.red(),bgColor.green(),bgColor.blue()),
                    PIIButton.COMMAND: each.Command,
                    PIIButton.COMMANDTYPE: each.CommandsType
                }
                nodeList.append(item)

        rawData = {
            PII.VERSION:"2.0.0",
            PII.BACKGROUND: image_data,
            PII.NODES: nodeList
        }
        return rawData
    def set_raw(self, data=dict):
        '''
        set the scene information. (information from .pii)

        Parameters
        ----------
        data: (dict)
            Dictionary of date from .pii file.
        '''
        if data:
            if data[PII.VERSION] == "1.0.0":
                self.load_1_0_0(data)
            if data[PII.VERSION] == "2.0.0":
                self.load_2_0_0(data)
    Raw = property(get_raw,set_raw)

    def get_namespace(self):
        '''
        Get namespace of all PickNode.

        Return
        ------
        out: (list)
            List of namespaces.
        '''
        namespaceList = []
        for each in self._scene.items():
            if type(each) == PickNode:
                valueList = each.Items
                for sObj in valueList:
                    if ":" in sObj:
                        group = sObj.split(":")[:-1]
                        for index in range(len(group)):
                            namespaceList.append(":".join(group[:index+1]))
        return list(set(namespaceList))
    def set_namespace(self, data=dict):
        '''
        Set namespace of all PickNode.

        Parameters
        ----------
        data: (dict)
            Dictionary of namespace with value of new namespace.
        '''
        for each in self._scene.items():
            if type(each) == PickNode:
                valueList = each.Items
                newValue = list()
                for sObj in valueList:
                    if ":" in sObj:
                        # namesapce
                        nameS = ":".join(sObj.split(":")[:-1])
                        # object name
                        object_name = sObj.split(":")[-1]
                        keys = data.keys()
                        keys.sort(reverse=True)
                        for key in keys:
                            if key in nameS:
                                nameS = nameS.replace(key,data[key],1)
                        # making sure doesn't start with ':'
                        nameS = nameS[1:] if nameS.startswith(":") else nameS
                        # add the object to namespace
                        nameS = ":".join([nameS,object_name]) if nameS else object_name
                        newValue.append(nameS)
                    else:
                        newValue.append(sObj)
                each.Items = newValue
    Namespace = property(get_namespace, set_namespace)

    def get_NSHistory(self):
        return self._namespace
    def set_NSHistory(self, name=str):
        self._namespace = name
    NamespaceHistory = property(get_NSHistory,set_NSHistory)

    def get_highlight(self):
        return 
    def set_highlight(self, data=list):
        if data:
            for each in self._scene.items():
                # QApplication.processEvents()
                if type(each) == PickNode:
                    for item in data:
                        if item in each.Items:
                            each.Highlight = True
                            break
                        else:
                            each.Highlight = False
        else:
            for each in self._scene.items():
                if type(each) == PickNode:
                    each.Highlight = False
    Highlight = property(get_highlight,set_highlight)

    def clear_scene(self):
        '''
        Clear the scene.
        '''
        self._orderSelected = list()
        self._scene.clear()
        self._backgroundNode = QGraphicsPixmapItem()
        self._scene.addItem(self._backgroundNode)
        self.reset_view()
    def is_changed(self):
        '''
        Check for the scene changes.
        '''
        if self._backgroundNode.pixmap():
            return True
        elif len(self._scene.items()) > 1:
            return True
        return False

    def load_1_0_0(self, data=dict):
        '''
        Load v1.0.0 of .pii version file.

        Parameters
        ----------
        data: (dict)
            Dictionary of date from .pii file.
        '''
        if data[PII.BACKGROUND]:
            # Import Image Data
            newPix = QPixmap()
            newPix.loadFromData(QByteArray.fromBase64(data[PII.BACKGROUND].encode('ascii')), "PNG")
            self._backgroundNode.setPixmap(newPix)

        for each in data[PII.NODES]:
            if each["type"] == PIINode.PICK:
                self.create_node(
                    text = each[PIIPick.TEXT],
                    size = each[PIIPick.SIZE],
                    textColor = QColor(*each[PIIPick.COLOR]),
                    bgColor = QColor(*each[PIIPick.BACKGROUND]),
                    position = QPointF(*each[PIIPick.POSITION]),
                    items = each[PIIPick.SELECTION]
                )
            elif each["type"] == PIINode.BUTTON:
                self.create_button(
                    position = QPointF(*each[PIIButton.POSITION]),
                    text = each[PIIButton.TEXT],
                    size = each[PIIButton.SIZE],
                    textColor = QColor(*each[PIIButton.COLOR]),
                    bgColor = QColor(*each[PIIButton.BACKGROUND]),
                    cmd = each[PIIButton.COMMAND],
                    cmdType = each[PIIButton.COMMANDTYPE]
                )

    def load_2_0_0(self, data=dict):
        '''
        Load v2.0.0 of .pii version file.

        Parameters
        ----------
        data: (dict)
            Dictionary of date from .pii file.
        '''
        if data[PII.BACKGROUND]:
            # Import Image Data
            newPix = QPixmap()
            newPix.loadFromData(QByteArray.fromBase64(data[PII.BACKGROUND].encode('ascii')), "PNG")
            self._backgroundNode.setPixmap(newPix)

        for each in data[PII.NODES]:
            if each["type"] == PIINode.PICK:
                self.create_node(
                    text = each[PIIPick.TEXT],
                    size = each[PIIPick.SIZE],
                    textColor = QColor(*each[PIIPick.COLOR]),
                    bgColor = QColor(*each[PIIPick.BACKGROUND]),
                    position = QPointF(*each[PIIPick.POSITION]),
                    items = each[PIIPick.SELECTION],
                    shape = each[PIIPick.SHAPE]
                )
            elif each["type"] == PIINode.BUTTON:
                self.create_button(
                    position = QPointF(*each[PIIButton.POSITION]),
                    text = each[PIIButton.TEXT],
                    size = each[PIIButton.SIZE],
                    textColor = QColor(*each[PIIButton.COLOR]),
                    bgColor = QColor(*each[PIIButton.BACKGROUND]),
                    cmd = each[PIIButton.COMMAND],
                    cmdType = each[PIIButton.COMMANDTYPE]
                )

    def set_nodes_bg_color(self, color=QColor):
        '''
        Set background color of selected nodes.

        Parameters
        ----------
        color: (QColor)
            QColor value.
        '''
        self._defaultColor = color
        for each in self._scene.selectedItems():
            each.Background = color
        self.update()
    def set_nodes_font_color(self, color=QColor):
        '''
        Set font color of selected nodes.

        Parameters
        ----------
        color: (QColor)
            QColor value.
        '''
        self._defaultTextColor = color
        for each in self._scene.selectedItems():
            each.setDefaultTextColor(color)
    def set_nodes_font_size(self, size=int):
        '''
        Set font size of selected nodes.

        Parameters
        ----------
        size: (int)
            font size.
        '''
        self._defaultTextSize = size
        for each in self._scene.selectedItems():
            font = each.font()
            font.setPointSize(size)
            each.setFont(font)
    def set_nodes_text(self, text=str):
        '''
        Set text for selected nodes.

        Parameters
        ----------
        text: (str)
            text for the node.
        '''
        self._defaultText = text
        for each in self._scene.selectedItems():
            each.setPlainText(text)

    def set_nodes_shape(self, shape=str):
        '''
        Set shape for selected nodes.

        Parameters
        ----------
        shape: (str)
            name for the shape.
        '''
        for each in self._scene.selectedItems():
            if isinstance(each, PickNode):
                each.Shape = shape
