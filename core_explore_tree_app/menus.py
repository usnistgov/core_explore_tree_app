""" Add Explore tree in main menu
"""

from menu import Menu, MenuItem

from core_explore_tree_app.settings import EXPLORE_TREE_MENU_NAME


Menu.add_item(
    "main", MenuItem(EXPLORE_TREE_MENU_NAME, "core_explore_tree_index")
)
