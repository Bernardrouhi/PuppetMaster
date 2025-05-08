from PuppetMaster.UI.PuppetMasterMain import PuppetMasterMainWindow
from PuppetMaster.Core.mayaHelper import mayaMainWindow

APP = None


def main() -> None:
    global APP
    APP = PuppetMasterMainWindow(parent=mayaMainWindow())
    APP.show()
