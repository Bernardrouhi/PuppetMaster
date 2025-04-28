from PySideWrapper.QtWidgets import *
from PySideWrapper.QtCore import *

from PuppetMaster.Core.qnodes import (CommandType, PIIButton)
from PuppetMaster.Core.mayaHelper import (runPython, runMel)


class CommandDialog(QDialog):
    def __init__(self, text: str, cmd: str, cmdType: str = CommandType.PYTHON, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self.cmd = cmd
        self.cmdType = cmdType
        self.text = text
        self.initUI()

    def initUI(self) -> None:
        mainLayout = QGridLayout(self)
        mainLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        mainLayout.setColumnStretch(0, 0)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 1)
        self.setLayout(mainLayout)

        nameText = QLabel('Name:')
        nameText.setAlignment(Qt.AlignRight)
        self.nameIn = QLineEdit()
        self.nameIn.setText(self.text)
        mainLayout.addWidget(nameText, 0, 0)
        mainLayout.addWidget(self.nameIn, 0, 1, 1, 3)

        langText = QLabel('Language:')
        langText.setAlignment(Qt.AlignRight)
        self.pyCheck = QRadioButton(CommandType.PYTHON)
        if self.cmdType == self.pyCheck.text():
            self.pyCheck.setChecked(True)
        self.melCheck = QRadioButton(CommandType.MEL)
        if self.cmdType == self.melCheck.text():
            self.melCheck.setChecked(True)
        mainLayout.addWidget(langText, 1, 0)
        mainLayout.addWidget(self.pyCheck, 1, 1)
        mainLayout.addWidget(self.melCheck, 1, 3)

        cmdText = QLabel('Command:')
        cmdText.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.cmdIn = QTextEdit()
        self.cmdIn.setPlainText(self.cmd)
        mainLayout.addWidget(cmdText, 2, 0)
        mainLayout.addWidget(self.cmdIn, 2, 1, 1, 3)

        okBtn = QPushButton("OK")
        okBtn.clicked.connect(self.accept)
        testBtn = QPushButton("Test")
        testBtn.clicked.connect(self.onTest)
        cancelBtn = QPushButton("Cancel")
        cancelBtn.clicked.connect(self.reject)

        mainLayout.addWidget(okBtn, 3, 1, 1, 1)
        mainLayout.addWidget(testBtn, 3, 2, 1, 1)
        mainLayout.addWidget(cancelBtn, 3, 3, 1, 1)
        self.setWindowTitle("Edit Command")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def onTest(self) -> None:
        cmdType = self.pyCheck.text() if self.pyCheck.isChecked() == True else self.melCheck.text()
        cmd = self.cmdIn.toPlainText()
        name = self.nameIn.text()
        if cmdType == CommandType.PYTHON:
            runPython(cmd)
        elif cmdType == CommandType.MEL:
            runMel(cmd)

    def get_raw(self) -> dict:
        cmdType = self.pyCheck.text() if self.pyCheck.isChecked() == True else self.melCheck.text()
        cmd = self.cmdIn.toPlainText()
        name = self.nameIn.text()
        return {
            PIIButton.TEXT: name,
            PIIButton.COMMAND: cmd,
            PIIButton.COMMANDTYPE: cmdType
        }

    Raw = property(get_raw)
