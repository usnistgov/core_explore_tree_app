""" Data api for core explore tree app
"""
from core_main_app.components.data.models import Data


def get_all_by_list_template(list_template):
    """ Get all data that belong to the template list.

    Args:
        list_template:

    Returns:

    """
    return Data.get_all_by_list_template(list_template)
