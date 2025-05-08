import os, json
from PuppetMaster.Core.PySideLibrary.QtWidgets import *
from PuppetMaster.Core.PySideLibrary.QtCore import Qt
from PuppetMaster.Core.env_handler import (get_PMTemplateDir)


class TemplateDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_ui()

    def _init_ui(self) -> None:
        mainLayout = QGridLayout(self)
        mainLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        mainLayout.setColumnStretch(0, 0)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        self.setLayout(mainLayout)

        line = 0
        nameText = QLabel('Name:')
        nameText.setAlignment(Qt.AlignRight)
        self.nameIn = QLineEdit()
        mainLayout.addWidget(nameText, line, 0)
        mainLayout.addWidget(self.nameIn, line, 1, 1, 2)

        line += 1
        tempText = QLabel('Template:')
        tempText.setAlignment(Qt.AlignRight)
        self.tempCombo = QComboBox()
        self.tempCombo.addItem('[NO TEMPLATE]', 0)
        self._read_templates()
        mainLayout.addWidget(tempText, line, 0)
        mainLayout.addWidget(self.tempCombo, line, 1, 1, 2)

        line += 1
        okBtn = QPushButton("Create")
        okBtn.clicked.connect(self.accept)
        cancelBtn = QPushButton("Cancel")
        cancelBtn.clicked.connect(self.reject)

        mainLayout.addWidget(okBtn, line, 1, 1, 1)
        mainLayout.addWidget(cancelBtn, line, 2, 1, 1)
        self.setWindowTitle("New Picker Interface Information")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def _read_templates(self) -> None:
        template_dir = get_PMTemplateDir()
        if os.path.exists(template_dir):
            files = os.walk(template_dir).next()[2]
            for each in files:
                if each.lower().endswith(".pii"):
                    self.tempCombo.addItem(each, each)

    def get_raw(self) -> dict:
        name = self.nameIn.text()
        template_dir = get_PMTemplateDir()
        template = self.tempCombo.currentText()
        data = {}
        if template != "[NO TEMPLATE]":
            path = os.path.join(template_dir, template)
            with open(path, 'r') as outfile:
                data = json.load(outfile)
        return {
            'name': name,
            'data': data
        }

    Raw = property(get_raw)
