"""Core Explore tree App Settings
"""
from django.conf import settings

if not settings.configured:
    settings.configure()

# MENU
EXPLORE_TREE_MENU_NAME = getattr(settings, 'EXPLORE_TREE_MENU_NAME', 'Explore tree')