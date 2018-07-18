""" Menu configuration for core_explore_tree_app.
"""
from django.core.urlresolvers import reverse
from menu import Menu, MenuItem

from core_explore_tree_app.settings import EXPLORE_TREE_MENU_NAME

ontology_children = (
    MenuItem("OWL files", reverse("admin:core_exploration_tree_app_query_ontology"), icon="list"),
    MenuItem("Upload New OWL", reverse("admin:core_exploration_tree_app_upload_query_ontology"), icon="upload"),

)

Menu.add_item(
    "admin", MenuItem("EXPLORATION TREE", None, children=ontology_children)
)

Menu.add_item(
    "main", MenuItem(EXPLORE_TREE_MENU_NAME, "core_explore_tree_index")
)
