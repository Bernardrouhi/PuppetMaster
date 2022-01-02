from PySide2.QtWidgets import (QWidgetAction, QWidget, QPushButton, QGridLayout, QMenu, QButtonGroup)
from PySide2.QtCore import Qt, QPoint, Signal
from PySide2.QtGui import (QColor, QPixmap, QPainter, QIcon)

COLOR_PALETTE = [
    QColor(179,102,102),QColor(255,128,128),QColor(255,0,0),QColor(191,0,0),QColor(128,0,0),QColor(0,0,0),
    QColor(179,141,102),QColor(225,192,128),QColor(255,128,0),QColor(191,95,0),QColor(128,64,0),QColor(23,23,23),
    QColor(179,179,102),QColor(225,225,128),QColor(255,225,0),QColor(191,191,0),QColor(128,128,0),QColor(46,46,46),
    QColor(141,179,102),QColor(192,225,128),QColor(128,225,0),QColor(95,191,0),QColor(94,128,0),QColor(69,69,69),
    QColor(102,179,102),QColor(128,225,128),QColor(0,225,0),QColor(0,191,0),QColor(0,128,0),QColor(93,93,93),
    QColor(102,179,141),QColor(128,225,192),QColor(0,225,128),QColor(0,191,95),QColor(0,128,64),QColor(116,116,116),
    QColor(102,179,179),QColor(128,225,255),QColor(0,225,255),QColor(0,191,191),QColor(0,128,128),QColor(139,139,139),
    QColor(102,141,179),QColor(128,192,255),QColor(0,128,255),QColor(0,95,191),QColor(0,64,128),QColor(162,162,162),
    QColor(102,102,179),QColor(128,128,255),QColor(0,0,255),QColor(0,0,191),QColor(0,0,128),QColor(186,186,186),
    QColor(141,102,179),QColor(192,128,255),QColor(128,0,255),QColor(95,0,191),QColor(64,0,128),QColor(209,209,209),
    QColor(179,102,179),QColor(255,128,255),QColor(255,0,255),QColor(191,0,191),QColor(128,0,128),QColor(232,232,232),
    QColor(179,102,141),QColor(255,128,192),QColor(255,0,128),QColor(191,0,95),QColor(128,0,64),QColor(255,255,255)
]

BW_PALETTE = [QColor(0,0,0),QColor(255,255,255)]

class QPushColorButton(QPushButton):
    colorSelected = Signal(QColor)
    def __init__(self, parent=None, columns=int(0), rows=int(0), palette=list):
        super(QPushColorButton, self).__init__(parent, "")
        self.setMaximumWidth(25)
        self.setMaximumHeight(25)
        self.currentColor = QColor(255,255,255)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.palette = palette
        self._columns = columns
        self._rows = rows

    def paintEvent(self,event):
        super(QPushColorButton, self).paintEvent(event)
        size = 13
        height = (self.height() - size)/2
        width = (self.width() - size)/2
        qp = QPainter(self)
        # qp.begin(self)
        qp.setPen(Qt.NoPen)
        qp.setBrush(self.currentColor)
        qp.drawRect(width, height, size, size)

    def color_menu(self, QPos=list):
        '''
        Show color menu.

        Parameters
        ----------
        QPos: (list)
            list of x and y location.
        '''
        self.mainMenu = QMenu()
        self.mainMenu.setStyleSheet("QMenu {background-color: #222222;}")
        colorAction = ColorAction(self.mainMenu, self._columns, self._rows, self.palette)
        colorAction.colorSelected.connect(self.handleColorSelected)
        self.mainMenu.addAction(colorAction)

        pos = self.mapToGlobal(QPoint(0,0))
        self.mainMenu.move(pos + QPos)
        self.mainMenu.show()

    def get_palette(self):
        return self.palette
    def set_palette(self, value=list):
        self.palette = value
    Palette= property(get_palette, set_palette)

    def get_columns(self):
        return self._columns
    def set_columns(self, value=int):
        self._columns = value
    Columns = property(get_columns,set_columns)

    def get_rows(self):
        return self._rows
    def set_rows(self, value=int):
        self._rows = value
    Rows = property(get_rows,set_rows)

    def handleColorSelected(self, color=QColor):
        self.currentColor = color
        self.colorSelected.emit(color)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.color_menu(event.pos())
        super(QPushColorButton, self).mousePressEvent(event)

    def get_current_color(self):
        return self.currentColor
    def set_current_color(self, color=QColor):
        self.currentColor = color
        self.update()
    CurrentColor = property(get_current_color,set_current_color)


class ColorAction(QWidgetAction):
    colorSelected = Signal(QColor)
    def __init__(self, parent=None, columns=int(0), rows=int(0), palette=list):
        # QWidgetAction.__init__(self, parent)
        super(ColorAction, self).__init__(parent)
        self._columns = columns
        self._rows = rows
        if columns < 1:
            self._columns = len(palette)
        if rows < 1:
            self._rows = len(palette)
        self.palette = palette
        self.init()

    def init(self):
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        num = 0
        self.ColorDict = dict()
        self.ButtonList = QButtonGroup()
        for column in range(self._columns):
            for row in range(self._rows):
                if num < len(self.palette):
                    newColor = self.palette[num]
                    button = QPushButton('')
                    button.setContentsMargins(0,0,0,0)
                    button.setStyleSheet("padding: 0px;margin: 0px;")
                    button.setFixedSize(20,20)
                    self.ColorDict[button] = self.palette[num]
                    self.ButtonList.addButton(button)
                    pixmap = QPixmap(20, 20)
                    pixmap.fill(newColor)
                    button.setIcon(QIcon(pixmap))
                    layout.addWidget(button, row, column)
                    num+=1
                else:
                    break
        self.ButtonList.buttonClicked.connect(self.handleButton)
        self.setDefaultWidget(widget)

    def handleButton(self, buttonID=QPushButton):
        self.parent().hide()
        self.colorSelected.emit(self.ColorDict[buttonID])
