import sys, os
from typing import List
from PuppetMaster.Core.PySideLibrary.QtGui import *


class PkgResources:
    iconDir: List[str] = ["..", "Resources", "Icons"]

    @classmethod
    def _collectPath(cls, directories: List[str]) -> str:
        """
        Collect the path
        """
        return os.path.abspath(os.path.join(os.path.dirname(sys.modules[cls.__module__].__file__), *directories))

    @classmethod
    def icon(cls, fileName: str) -> str:
        """
        Get a pure icon path.
        :param fileName: Name of the icon with extension.
        """
        return os.path.abspath(os.path.join(cls._collectPath(cls.iconDir), fileName).replace("\\", "/"))

    @classmethod
    def qIcon(cls, fileName: str) -> QIcon:
        """
        Get icon as QIcon.
        :param fileName: Name of the icon with extension.
        """
        return QIcon(cls.icon(fileName))
