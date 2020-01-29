from PySide2.QtWidgets import (QGraphicsItem, QStyleOptionGraphicsItem, 
                          QWidget, QGraphicsTextItem)
from PySide2.QtCore import Qt, Signal, QPointF, QSize
from PySide2.QtGui import (QColor, QPen, QPainter, QPainterPath, QLinearGradient,
                      QTextCursor, QBrush)
from uuid import uuid4
from icon import QIconSVG, iconSVG

IMAGE_FORMATS = (".jpeg", ".jpg", ".png", ".exr", ".gif")

class PII():
    BACKGROUND = "background"
    VERSION = "version"
    NODES = "nodes"

class PIINode():
    PICK = "text_node"
    BUTTON = "button_node"

class PIIPick():
    TEXT = "text"
    POSITION = "position"
    COLOR = "text_color"
    BACKGROUND = "background_color"
    TYPE = 'type'
    SIZE = 'size'
    SELECTION = "selection"
    SHAPE = 'shape'

class PickShape():
    SQUARE = "square"
    CIRCLE = "circle"
    PLUS = "plus"
    TRIANGLE = "triangle"

class PIIButton():
    TEXT = "text"
    POSITION = "position"
    COLOR = "text_color"
    BACKGROUND = "background_color"
    TYPE = 'type'
    SIZE = 'size'
    COMMAND = "command"
    COMMANDTYPE = "command_type"

class CommandType():
    PYTHON = "python"
    MEL = "mel"

class PickNode(QGraphicsTextItem):
    onClick = Signal()
    onSelected = Signal(list)
    onAddToStack = Signal()
    onRemoveFromStack = Signal()
    def __init__(self, *args, **kwargs):
        super(PickNode, self).__init__(*args, **kwargs)
        self._highlight = False
        self.init()

    def init(self):
        self._model = {
            'bgColor': QColor(255,255,255),
            'command': str(),
            'commandsType': CommandType.PYTHON,
            'item':list(),
            'shape': 'square',
            'id' : str(uuid4())
        }
        self.update_tooltip()

    def set_Id(self, value=str):
        self._model["id"] = value
    def get_id(self):
        return self._model["id"]
    id = property(get_id, set_Id)

    def get_brush(self):
        return self._model["bgColor"]
    def set_brush(self, value=QColor):
        self._model["bgColor"] = QColor(value)
        self.update()
    Background = property(get_brush, set_brush)
    def get_items(self):
        return self._model["item"]
    def set_items(self, names=list):
        self._model["item"] = names
        self.update_tooltip()
    Items = property(get_items, set_items)

    def get_shape(self):
        return self._model["shape"]
    def set_shape(self, name=str):
        self._model["shape"] = name
        self.update()
    Shape = property(get_shape, set_shape)

    def update_tooltip(self):
        if self._model["item"]:
            self.setToolTip("\n".join(self._model["item"])) 

    def paint(self, painter=QPainter, option=QStyleOptionGraphicsItem, widget=QWidget):
        if self._model["shape"] == PickShape.SQUARE:
            self.draw_square(painter)
            # text
            super(PickNode, self).paint(painter, option, widget)
        elif self._model["shape"] == PickShape.CIRCLE:
            self.draw_circle(painter)
        elif self._model["shape"] == PickShape.TRIANGLE:
            self.draw_triangle(painter)
        elif self._model["shape"] == PickShape.PLUS:
            self.draw_plus(painter)


    def draw_square(self, painter=QPainter):
        brush = QBrush()
        # background
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(self._model["bgColor"])
        painter.setBrush(brush)
        painter.drawRect(self.boundingRect())

        # Highlighted
        painter.setPen(Qt.NoPen)
        if self._highlight:
            brush.setStyle(Qt.SolidPattern)
            # brush.setColor(QColor(192,255,0))
            brush.setColor(QColor(255,0,0))
        else:
            brush.setStyle(Qt.SolidPattern)
            brush.setColor(QColor(224,224,224))
        boundry = self.boundingRect()
        boundry.setTopRight(boundry.topLeft() + QPointF(4.0,0))
        boundry.setBottomRight(boundry.bottomLeft() + QPointF(4.0,0))
        painter.setBrush(brush)
        painter.drawRect(boundry)

        boundry = self.boundingRect()
        boundry.setTopLeft(boundry.topRight() - QPointF(4.0,0))
        boundry.setBottomLeft(boundry.bottomRight() - QPointF(4.0,0))
        painter.setBrush(brush)
        painter.drawRect(boundry)

    def draw_circle(self, painter=QPainter):
        brush = QBrush()
        # Highlighted
        painter.setPen(Qt.NoPen)
        if self._highlight:
            brush.setStyle(Qt.SolidPattern)
            brush.setColor(QColor(255,0,0))
        else:
            brush.setStyle(Qt.SolidPattern)
            brush.setColor(QColor(224,224,224))
        boundry = self.boundingRect()
        painter.setBrush(brush)
        painter.drawEllipse(boundry)

        # background
        brush.setColor(self._model["bgColor"])
        painter.setBrush(brush)
        boundry = self.boundingRect()
        offset = 2
        painter.drawEllipse(boundry.x()+offset, boundry.y()+offset, boundry.width()-(offset*2),boundry.height()-(offset*2))


    def draw_triangle(self, painter=QPainter):
        brush = QBrush()
        # Highlighted
        painter.setPen(Qt.NoPen)
        if self._highlight:
            brush.setStyle(Qt.SolidPattern)
            brush.setColor(QColor(255,0,0))
        else:
            brush.setStyle(Qt.SolidPattern)
            brush.setColor(QColor(224,224,224))
        boundry = self.boundingRect()
        painter.setBrush(brush)
        path = QPainterPath()
        p1 = QPointF(boundry.center().x(),0)
        p2 = QPointF(boundry.width(),boundry.height())
        p3 = QPointF(0,boundry.height())
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        path.lineTo(p1)
        painter.drawPath(path)

        # background
        brush.setColor(self._model["bgColor"])
        painter.setBrush(brush)
        percentage = 8
        wOffset = (percentage * boundry.width())/100
        hOffset = (percentage * boundry.height())/100
        path = QPainterPath()
        p1 = QPointF(boundry.center().x(),hOffset)
        p2 = QPointF(boundry.width()-wOffset,boundry.height()-hOffset)
        p3 = QPointF(wOffset,boundry.height()-hOffset)
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        path.lineTo(p1)
        painter.drawPath(path)

    def draw_plus(self, painter=QPainter):
        brush = QBrush()
        # Highlighted
        painter.setPen(Qt.NoPen)
        if self._highlight:
            brush.setStyle(Qt.SolidPattern)
            brush.setColor(QColor(255,0,0))
        else:
            brush.setStyle(Qt.SolidPattern)
            brush.setColor(QColor(224,224,224))
        boundry = self.boundingRect()
        painter.setBrush(brush)
        path = QPainterPath()
        widthSec = boundry.width()/3
        heightSec = boundry.height()/3
        path.moveTo(widthSec,0)
        path.lineTo(widthSec*2,0)
        path.lineTo(widthSec*2,heightSec)
        path.lineTo(widthSec*3,heightSec)
        path.lineTo(widthSec*3,heightSec*2)
        path.lineTo(widthSec*2,heightSec*2)
        path.lineTo(widthSec*2,heightSec*3)
        path.lineTo(widthSec,heightSec*3)
        path.lineTo(widthSec,heightSec*2)
        path.lineTo(0,heightSec*2)
        path.lineTo(0,heightSec)
        path.lineTo(widthSec,heightSec)
        path.lineTo(widthSec,0)
        painter.drawPath(path)

        # background
        brush.setColor(self._model["bgColor"])
        painter.setBrush(brush)
        offset = 4
        path = QPainterPath()
        widthSec = boundry.width()/3
        heightSec = boundry.height()/3
        path.moveTo(widthSec+offset,0+offset)
        path.lineTo((widthSec*2)-offset,0+offset)
        path.lineTo((widthSec*2)-offset,heightSec+offset)
        path.lineTo((widthSec*3)-offset,heightSec+offset)
        path.lineTo((widthSec*3)-offset,(heightSec*2)-offset)
        path.lineTo((widthSec*2)-offset,(heightSec*2)-offset)
        path.lineTo((widthSec*2)-offset,(heightSec*3)-offset)
        path.lineTo(widthSec+offset,(heightSec*3)-offset)
        path.lineTo(widthSec+offset,(heightSec*2)-offset)
        path.lineTo(0+offset,(heightSec*2)-offset)
        path.lineTo(0+offset,heightSec+offset)
        path.lineTo(widthSec+offset,heightSec+offset)
        path.lineTo(widthSec+offset,0+offset)
        painter.drawPath(path)

    def text_edit(self):
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus(Qt.MouseFocusReason)
        self.setSelected(True)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.text_highlight()

    def text_highlight(self):
        cursor = self.textCursor()
        cursor.setPosition(QTextCursor.Start, QTextCursor.MoveAnchor)
        cursor.setPosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.atEnd()
        self.setTextCursor(cursor)

    def clear_highlight(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange and value:
            self.onSelected.emit(self.get_items())
            self.onAddToStack.emit()
        elif value == 0:
            self.onRemoveFromStack.emit()
        return super(PickNode, self).itemChange(change,value)

    def get_highlight(self):
        return self._highlight
    def set_highlight(self, value=bool):
        self._highlight = value
        self.update()
    Highlight = property(get_highlight, set_highlight)

class ButtonNode(QGraphicsTextItem):
    onClicked = Signal(str, str)
    onSelected = Signal()
    def __init__(self, *args, **kwargs):
        super(ButtonNode, self).__init__(*args, **kwargs)
        self.setAcceptHoverEvents(True)
        self.init()

        self.isPressed = False
        self.editMode = True
        self.hover = False

    def init(self):
        self._model = {
            'bgColor': QColor(178,34,34),
            'command': str(),
            'commandsType': CommandType.PYTHON,
            'id' : str(uuid4())
        }
        self.update_tooltip()

    def get_brush(self):
        return self._model["bgColor"]
    def set_brush(self, value=QColor):
        self._model["bgColor"] = QColor(value)
        self.update()
    Background = property(get_brush, set_brush)

    def get_command(self):
        return self._model["command"]
    def set_command(self, cmd=str):
        self._model["command"] = cmd
    Command = property(get_command, set_command)

    def get_commandsType(self):
        return self._model["commandsType"]
    def set_commandsType(self, cmdType=str):
        self._model["commandsType"] = cmdType
        self.update_tooltip()
    CommandsType = property(get_commandsType, set_commandsType)

    def update_tooltip(self):
        self.setToolTip(self._model["command"]) 

    def paint(self, painter=QPainter, option=QStyleOptionGraphicsItem, widget=QWidget):
        corners = 5
        body = self.boundingRect()
        height = body.height()
        width = body.width()
        percentage = height/10
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(body,corners,corners)
        pen = QPen(QColor(255,255,255,100), 3) if self.hover and not self.isPressed else QPen(Qt.black, 0.1)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.fillPath(path, self._model["bgColor"])
        painter.drawPath(path)
        if not self.isPressed:
            grad = QLinearGradient(0, height, 0, height-percentage)
            grad.setColorAt(0, QColor(175,175,175,255))
            grad.setColorAt(1, QColor(175,175,175,0))
            path = QPainterPath()
            path.addRoundedRect(body,corners,corners)
            painter.setCompositionMode(QPainter.CompositionMode_Multiply)
            painter.setPen(Qt.NoPen)
            painter.fillPath(path,grad)
            painter.drawPath(path)

            grad = QLinearGradient(0, percentage, 0, 0)
            grad.setColorAt(1, QColor(255,255,255,255))
            grad.setColorAt(0, QColor(255,255,255,0))
            path = QPainterPath()
            path.addRoundedRect(body,corners,corners)
            painter.setCompositionMode(QPainter.CompositionMode_Overlay)
            painter.setPen(Qt.NoPen)
            painter.fillPath(path,grad)
            painter.drawPath(path)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
        else:
            path = QPainterPath()
            path.addRoundedRect(body,corners,corners)
            painter.setCompositionMode(QPainter.CompositionMode_Overlay)
            painter.setPen(Qt.NoPen)
            painter.fillPath(path,QColor(255,255,255))
            painter.drawPath(path)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
        super(ButtonNode, self).paint(painter, option, widget)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange and value:
            self.onSelected.emit()
        return super(ButtonNode, self).itemChange(change,value)

    def mousePressEvent(self, event):
        super(ButtonNode, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.isPressed = 1
            self.onClicked.emit(self.get_commandsType(),self.get_command())
            self.update()
    def mouseReleaseEvent(self, event):
        self.isPressed = 0
        self.update()
        super(ButtonNode, self).mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        QGraphicsTextItem.hoverEnterEvent(self, event)
        self.hover = True
        self.update()

    def hoverMoveEvent(self, event):
        QGraphicsTextItem.hoverMoveEvent(self, event)

    def hoverLeaveEvent(self, event):
        QGraphicsTextItem.hoverLeaveEvent(self, event)
        self.hover = False
        self.update() 
