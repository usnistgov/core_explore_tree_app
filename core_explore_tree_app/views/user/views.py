"""Explore tree app user views
"""
import json

from django.core.cache import caches
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED

import core_explore_tree_app.components.query_ontology.api as query_ontology_api
from core_explore_tree_app.components.navigation.api import create_navigation_tree_from_owl_file
from core_explore_tree_app.parser.renderer import render_navigation_tree
from core_main_app.commons import exceptions
from core_main_app.utils.rendering import render

navigation_cache = caches['navigation']
html_tree_cache = caches['html_tree']


@cache_page(600 * 15)
def core_explore_tree_index(request):
    """ Page that allows to see the exploration tree.

    Args:
        request:

    Returns:

    """
    # Not sure is needed
    if request.method != "GET":
        return HttpResponse({}, status=HTTP_405_METHOD_NOT_ALLOWED)

    try:
        # get the active ontology
        active_ontology = query_ontology_api.get_active()

        # get the navigation from the cache
        nav_key = active_ontology.id
        if nav_key in navigation_cache:
            navigation = navigation_cache.get(nav_key)
        else:
            # create the navigation
            navigation = create_navigation_tree_from_owl_file(active_ontology.content)
            navigation_cache.set(nav_key, navigation)

        # get the tree from the cache
        tree_key = navigation.id
        if tree_key in navigation_cache:
            html_tree = html_tree_cache.get(tree_key)
        else:
            # create the html tree
            html_tree = render_navigation_tree(navigation, active_ontology.template.id)
            html_tree_cache.set(tree_key, navigation)

    except exceptions.DoesNotExist as e_does_not_exist:
        error = {"message": e_does_not_exist.message}
        return HttpResponse(json.dumps(error), status=HTTP_404_NOT_FOUND)
    except Exception as e:
        # FIXME use logger e.message
        return HttpResponseBadRequest('An error occurred during the generation of the navigation tree.')

    context = {
        'navigation_tree': html_tree,
        'navigation_id': navigation.id
    }

    assets = {
        "js": [
            {
                "path": 'core_explore_tree_app/user/js/load_view.js',
                "is_raw": False
            },
            {
                "path": 'core_explore_tree_app/user/js/tree.js',
                "is_raw": True
            },
            {
                "path": 'core_explore_tree_app/user/js/resize_tree_panel.js',
                "is_raw": True
            },
            {
                "path": 'core_explore_tree_app/user/js/mock.js',
                "is_raw": True
            },
        ],
        "css": ['core_explore_tree_app/user/css/tree.css']
    }

    return render(request,
                  'core_explore_tree_app/user/navigation/explore_tree_wrapper.html',
                  assets=assets,
                  context=context)
