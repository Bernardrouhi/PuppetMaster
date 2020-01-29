import os 
from PySide2.QtGui import QIcon

def current_file_path():
    '''
    Getting the path of current file.

    Return
    ------
    out: (str)
        Path of current directory.
    '''
    return str(os.path.dirname(os.path.realpath(__file__)).replace("\\","/"))

def iconSVG(name=str()):
    '''
    Getting the icon path.

    Parameters
    ----------
    name: (str)
        Name of the icon.

    Return
    ------
    out: (str)
        Full path of icon.
    '''
    return "{0}/icons/{1}.svg".format(current_file_path(),name)

def QIconSVG(name=str()):
    '''
    Getting the icon path.

    Parameters
    ----------
    name: (str)
        Name of the icon.

    Return
    ------
    out: (QIcon)
        QIcon of full path of icon.
    '''
    return QIcon("{0}/icons/{1}.svg".format(current_file_path(),name))