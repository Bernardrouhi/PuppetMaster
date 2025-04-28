from typing import Optional
from PySideWrapper.QtWidgets import *
from PySideWrapper.QtCore import *


class NamespaceDialog(QDialog):
    def __init__(self, namespaceList: list, validList: list, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self.namespace = namespaceList
        self.validNamespace = validList
        self.namespace.sort()
        self.validNamespace.sort()
        self.model = {}
        self.initUI()

    def initUI(self) -> None:
        mainLayout = QGridLayout(self)
        mainLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # mainLayout.setColumnStretch(0,0)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        # mainLayout.setColumnStretch(3,1)
        self.setLayout(mainLayout)

        line = 0
        title = QLabel('Change Current Namespace to:')
        title.setAlignment(Qt.AlignLeft)
        mainLayout.addWidget(title, line, 0, 1, 3)

        line += 1
        for each in self.namespace:
            dyName = QLabel(each)
            dyCombo = QComboBox()
            dyCombo.setLineEdit(QLineEdit())
            for valName in self.validNamespace:
                dyCombo.addItem(valName, self.validNamespace.index(valName))
            dyCombo.setCurrentIndex(dyCombo.findText(each, Qt.MatchExactly))
            mainLayout.addWidget(dyName, line, 0, 1, 1)
            mainLayout.addWidget(dyCombo, line, 1, 1, 2)
            self.model[each] = dyCombo
            line += 1

        line += 1
        okBtn = QPushButton("OK")
        okBtn.clicked.connect(self.accept)
        cancelBtn = QPushButton("Cancel")
        cancelBtn.clicked.connect(self.reject)

        mainLayout.addWidget(okBtn, line, 1, 1, 1)
        mainLayout.addWidget(cancelBtn, line, 2, 1, 1)
        self.setWindowTitle("Choose Namespace")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def get_raw(self) -> dict:
        """
        Get the updated namespace.

        Return
        ------
        out: (dict)
            Get the dictionary of old namespace with vlaue of 
            new namespace.
        """
        raw = {}
        for each in self.model.keys():
            value = self.model[each].currentText()
            raw[each] = value
        return raw

    Raw = property(get_raw)
