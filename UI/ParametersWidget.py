from typing import Optional
from PySideWrapper.QtWidgets import *
from PySideWrapper.QtCore import *
from PySideWrapper.QtGui import *

from PuppetMaster.Core.qnodes import PickShape
from PuppetMaster.Core.PkgResources import PkgResources

from .QPushColorButton import QPushColorButton, COLOR_PALETTE, BW_PALETTE


class Parameters(QWidget):
    onChangeBGColor = Signal(QColor)
    onChangeFontColor = Signal(QColor)
    onChangeFontSize = Signal(int)
    onChangeText = Signal(str)
    onChangeShape = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._parent = parent

        # self.setMinimumHeight(1)
        self.setFixedHeight(35)
        self.setMinimumWidth(1)

        # ------------- Main Layout --------------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        main_layout.setAlignment(Qt.AlignTop)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # ------- Row 1 -------
        # ----------------------------------------
        allLayout = QHBoxLayout()
        allLayout.setContentsMargins(0, 0, 0, 0)
        allLayout.setSpacing(3)
        allLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Color
        colorLabel = QLabel(u"Color:")
        colorLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.color_btn = QPushColorButton(columns=0, rows=6, palette=COLOR_PALETTE)
        self.color_btn.colorSelected.connect(self.change_bg_color)

        # Size
        sizeLabel = QLabel(u"Size:")
        sizeLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.size_combo = QComboBox()
        for i in range(1, 100):
            self.size_combo.addItem(str(i), i)
        self.size_combo.activated.connect(self.change_font_size)

        # Shape
        shapeLabel = QLabel(u"Shape:")
        shapeLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.shape_combo = QComboBox()
        self.shape_combo.addItem(PkgResources.qIcon('square'), PickShape.SQUARE, PickShape.SQUARE)
        self.shape_combo.addItem(PkgResources.qIcon('circle'), PickShape.CIRCLE, PickShape.CIRCLE)
        self.shape_combo.addItem(PkgResources.qIcon('triangle'), PickShape.TRIANGLE, PickShape.TRIANGLE)
        self.shape_combo.addItem(PkgResources.qIcon('plus'), PickShape.PLUS, PickShape.PLUS)
        self.shape_combo.activated.connect(self.change_shape)

        # Name
        nameLabel = QLabel(u"Label:")
        nameLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.nameIn = QLineEdit()
        self.nameIn.textEdited.connect(self.change_name)
        self.textColor_btn = QPushColorButton(columns=1, rows=0, palette=BW_PALETTE)
        self.textColor_btn.colorSelected.connect(self.change_font_color)

        # Add widget to Layout
        allLayout.addWidget(colorLabel)
        allLayout.addWidget(self.color_btn)
        allLayout.addWidget(sizeLabel)
        allLayout.addWidget(self.size_combo)
        allLayout.addWidget(shapeLabel)
        allLayout.addWidget(self.shape_combo)
        allLayout.addWidget(nameLabel)
        allLayout.addWidget(self.nameIn)
        allLayout.addWidget(self.textColor_btn)

        main_layout.addLayout(allLayout)

    def change_name(self) -> None:
        """
        Sending Signal from "onChangeText" to change the text
        """
        self.onChangeText.emit(self.nameIn.text())

    def change_bg_color(self, color: QColor) -> None:
        """
        Sending Signal from "onChangeBGColor" to change the
        background color.

        Parameters
        ----------
        color: (QColor)
            QColor value to send over.
        """
        self.onChangeBGColor.emit(color)

    def change_font_color(self, color: QColor) -> None:
        """
        Sending Signal from "onChangeFontColor" to change the
        font color.

        Parameters
        ----------
        color: (QColor)
            QColor value to send over.
        """
        self.onChangeFontColor.emit(color)

    def change_font_size(self, value: int) -> None:
        """
        Sending Signal from "onChangeFontSize" to change the
        font size.
        """
        self.onChangeFontSize.emit(value + 1)

    def change_shape(self) -> None:
        """
        Sending Signal from "onChangeShape" to change the
        shape of node.
        """
        self.onChangeShape.emit(self.shape_combo.currentText())

    def update_param(self, text: str, fontSize: int, fontColor: QColor, bgColor: QColor, shapeName: str) -> None:
        """
        Update the UI parameters.

        Parameters
        ----------
        text: (str)
            Name of the node.
        fontSize: (int)
            Size of the font.
        fontColor: (QColor)
            Color of the font.
        bgColor: (QColor)
            Color of the background.
        """
        self.color_btn.CurrentColor = bgColor
        self.textColor_btn.CurrentColor = fontColor
        self.size_combo.setCurrentIndex(self.size_combo.findText(str(fontSize)))
        self.nameIn.setText(text)
        if shapeName:
            self.shape_combo.setCurrentIndex(self.shape_combo.findText(shapeName))
            self.shape_combo.setEnabled(True)
        else:
            self.shape_combo.setEnabled(False)
            self.shape_combo.setCurrentIndex(-1)

    def get_name(self) -> str:
        return self.nameIn.text()

    def set_name(self, value: str) -> None:
        self.nameIn.setText(value)

    Name = property(get_name, set_name)
