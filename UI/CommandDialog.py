from typing import Optional
from PuppetMaster.Core.PySideLibrary.QtWidgets import *
from PuppetMaster.Core.PySideLibrary.QtCore import *
from PuppetMaster.Core.qnodes import (CommandType, PIIButton)
from PuppetMaster.Core.mayaHelper import (runPython, runMel)


class CommandDialog(QDialog):
    def __init__(self, text: str, cmd: str, cmdType: CommandType = CommandType.PYTHON, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self._command = cmd
        self._language = cmdType
        self._title = text
        self._init_ui()

    def _init_ui(self) -> None:
        mainLayout = QGridLayout(self)
        mainLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        mainLayout.setColumnStretch(0, 0)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 1)
        self.setLayout(mainLayout)

        nameText = QLabel('Name:')
        nameText.setAlignment(Qt.AlignRight)
        self._titleIn = QLineEdit()
        self._titleIn.setText(self._title)
        mainLayout.addWidget(nameText, 0, 0)
        mainLayout.addWidget(self._titleIn, 0, 1, 1, 3)

        langText = QLabel('Language:')
        langText.setAlignment(Qt.AlignRight)
        mainLayout.addWidget(langText, 1, 0)

        self._languageGroup = QButtonGroup()
        for index, option in enumerate(CommandType):
            button  = QRadioButton(option.value)
            button.setProperty("enum", option)
            self._languageGroup.addButton(button)
            if option == self._language:
                button.setChecked(True)
            mainLayout.addWidget(button, 1, index + 1)

        cmdText = QLabel('Command:')
        cmdText.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self._commandIn = QTextEdit()
        self._commandIn.setPlainText(self._command)
        mainLayout.addWidget(cmdText, 2, 0)
        mainLayout.addWidget(self._commandIn, 2, 1, 1, 3)

        okBtn = QPushButton("OK")
        okBtn.clicked.connect(self.accept)
        testBtn = QPushButton("Test")
        testBtn.clicked.connect(self.run)
        cancelBtn = QPushButton("Cancel")
        cancelBtn.clicked.connect(self.reject)

        mainLayout.addWidget(okBtn, 3, 1, 1, 1)
        mainLayout.addWidget(testBtn, 3, 2, 1, 1)
        mainLayout.addWidget(cancelBtn, 3, 3, 1, 1)
        self.setWindowTitle("Edit Command")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def run(self) -> None:
        """ Run the current command. """
        cmdType = self.get_language()
        if cmdType == CommandType.PYTHON:
            runPython(self._commandIn.toPlainText())
        elif cmdType == CommandType.MEL:
            runMel(self._commandIn.toPlainText())

    def get_command(self) -> str:
        """ Get the current command. """
        return self._commandIn.toPlainText()

    def get_language(self) -> CommandType:
        """ Get the current language selected. """
        button: QRadioButton = self._languageGroup.checkedButton()
        cmdType: CommandType = button.property("enum")
        return cmdType

    def get_name(self) -> str:
        return self._titleIn.text()

    def get_raw(self) -> dict:
        return {
            PIIButton.TEXT: self.get_name(),
            PIIButton.COMMAND: self.get_command(),
            PIIButton.COMMANDTYPE: self.get_language()
        }

    Raw = property(get_raw)
