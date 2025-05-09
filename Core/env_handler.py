import os

PM_WORK_DIR = 'PM_ROOT_DIR'
PM_TEMPLATE_DIR = 'PM_TEMPLATES_DIR'


# Handling PM_TEMPLATE_DIR
def is_PMTemplateDir() -> bool:
    """
    Check if the PM_TEMPLATE_DIR key exist in environment variables.

    Return
    ------
    out: (boolean)
        True if the key exists in environment varibales, otherwise False.
    """
    return True if PM_TEMPLATE_DIR in os.environ else False


def get_PMTemplateDir() -> str:
    """
    Get the templates path from environemnt variables.

    Return
    ------
    out: (str)
        Get the project path
    """
    return os.getenv(PM_TEMPLATE_DIR, "")


# Handling PM_WORK_DIR
def is_PMWorkDir() -> bool:
    """
    Check if the PM_WORK_DIR key exist in environment variables.

    Return
    ------
    out: (boolean)
        True if the key exists in environment varibales, otherwise False.
    """
    return True if PM_WORK_DIR in os.environ else False


def get_PMWorkDir() -> str:
    """
    Get the work file path from environemnt variables.

    Return
    ------
    out: (str)
        Get the project path
    """
    return os.getenv(PM_WORK_DIR, "")
