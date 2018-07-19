""" Ajax calls for the exploration tree
"""
import json

from bson import ObjectId
from django.core.cache import caches
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from rest_framework.status import HTTP_400_BAD_REQUEST

from core_explore_tree_app.components.data import query
from core_explore_tree_app.components.navigation import api as navigation_api
from core_explore_tree_app.components.navigation import operations as navigation_operations
from core_explore_tree_app.parser import processview as parser_processview
from core_explore_tree_app.utils.xml.projection import get_projection
from core_main_app.components.data.models import Data

leaf_cache = caches['leaf']
branch_cache = caches['branch']
link_cache = caches['link']

# list of ordered dict = results of queries done on the main queried document
my_listof_ordereddicts_tab = []
# list of ordered dict = results of queries done on other queried documents
my_listof_ordereddicts_cross_docs_tab = []
list_od_dwnld_files = []
# list of currentNode_docId
my_tab = []

# list of list(tag,results) resulting on queries done on the other queried documents
# (corresponding to the data linked to a file in the tree)
my_list_of_cross_results_f = []
mystring = "MYSTRINGG"
# number of nodes reached for the xml that need to be built
sz = 0


@cache_page(600 * 15)
def load_view(request):
    """ Load view entry point

    Args:
        request:

    Returns:

    """
    # nav_id parameter is mandatory, if it doesn't exist we delete other parameters to raise and error
    if "nav_id" not in request.POST:
        error = {"message": "Request is malformed. nav_id is mandatory"}
        return HttpResponse(json.dumps(error), status=HTTP_400_BAD_REQUEST)

    # retrieve all the parameters from the request
    nav_id = request.POST.get('nav_id', None)
    node_id = request.POST.get('node_id', None)
    doc_id = request.POST.get('doc_id', None)
    ref_node_id = request.POST.get('ref_node_id', None)

    # click on a document in the tree
    if node_id is not None and doc_id is not None:
        node_name = get_node_name(node_id)
        c_id = str(node_name) + '_' + str(doc_id)
        # Get the document from the cache if this one had ever been accessed
        if c_id in leaf_cache:
            load_doc = leaf_cache.get(c_id)
        # Else :Query the database, process the documents
        else:
            load_doc = _load_data_view(node_id, nav_id, doc_id)
            leaf_cache.set(c_id, load_doc)

    # click on a node in the tree
    elif node_id is not None:
        if node_id in branch_cache:
            load_doc = branch_cache.get(node_id)
        else:
            load_doc = _load_branch_view(request)
            branch_cache.set(node_id, load_doc)

    # click on a link in a document (build id)
    elif ref_node_id is not None and doc_id is not None:
        c_id = ref_node_id + '_' + doc_id
        if c_id in link_cache:
            load_doc = link_cache.get(c_id)
        else:
            load_doc = _load_data_view(ref_node_id, nav_id, doc_id, False)
            link_cache.set(c_id, load_doc)

    else:
        error = {"message": "Request is malformed."}
        return HttpResponse(json.dumps(error), status=HTTP_400_BAD_REQUEST)

    # return the loaded data
    if load_doc is not None:
        return render(request, "core_explore_tree_app/user/explore_tree/view.html", load_doc)


def _load_branch_view(request):
    """ Load view for a branch

    Args:
        request:

    Returns:

    """
    # Retrieve the view annotation
    navigation_node = navigation_api.get_by_id(request.POST["node_id"])
    filters = navigation_operations.retrieve_navigation_filters(navigation_node)

    # FIXME modified query part to execute query directly
    documents = []
    query_documents = query.execute_query(filters, "id")

    for query_doc in query_documents:
        documents.append(query_doc.id)
    # Display XML file if "projection_view" annotation is not configured
    if "view" not in navigation_node.options:
        error = {
            "message": "'cql:view' annotation does not exist for this branch."
        }

        return HttpResponse(json.dumps(error), HTTP_400_BAD_REQUEST)

    branch_views = json.loads(navigation_node.options["view"])

    name = navigation_node.name.split('#')[1] if '#' in navigation_node.name else navigation_node.name
    view_data = {
        "header": name,
        "type": "branch",
        "views": []
    }

    for branch_view in branch_views:
        result_data = {
            "title": branch_view["title"],
            "data": parser_processview.processviewdocidlist(request.POST["nav_id"], documents, branch_view["data"])
        }

        view_data["views"].append(result_data)

    return render(request, "explore_tree/components/view.html", view_data)


def _load_data_view(node_id, nav_id, data_id, from_tree=True):
    """ Load view for a data, from a tree or a link

    Args:
        node_id:
        nav_id:
        data_id:
        from_tree:

    Returns:

    """
    if not from_tree:
        navigation_node = navigation_operations.get_navigation_node_for_document(node_id, data_id)
    else:
        navigation_node = navigation_api.get_by_id(node_id)

    # Initialize parameters in order to download later some information
    navigation_name2 = node_id
    xml_document = Data.get_by_id(data_id)
    projection_views = json.loads(navigation_node.options["projection_view"])

    view_data = {
        "header": xml_document.title,
        "type": "leaf",
        "views": []
    }
    # Initialize parameters in order to download later some information
    my_listof_ordereddicts_cross_docs2 = []
    my_listof_ordereddicts2 = []
    my_list_of_cross_results = []
    # Send the annotation to the processor and collect the data
    for projection_view in projection_views:
        result_data = {
            "title": projection_view["title"],
            "data": None
        }

        # FIXME better handling of x-queries
        if "query" in projection_view.keys():

            my_projections = []
            # Get the names of the tags tag need to be displayed
            for value in projection_view["data"]:
                my_projections.append(value.get('path'))

            result_data["data"] = parser_processview.process_cross_query(nav_id,
                                                                         data_id,
                                                                         projection_view["query"],
                                                                         projection_view["data"])
            # Other quiered documents
            quiered_docs = parser_processview.ids_docs_to_querys
            for id_doc in quiered_docs:
                other_doc_query = {
                    "_id": ObjectId(id_doc)
                }

                for projection in my_projections:

                    proj_co = {
                        my_projections[my_projections.index(projection)]: 1
                    }
                    res_co = Data.execute_query(other_doc_query).only(proj_co.keys()[0])

                    try:

                        doc_projco = get_projection(res_co[0])
                        s = str(my_projections[my_projections.index(projection)])
                        y = s.split(".")
                        attribute = y[len(y) - 1]

                        my_list_of_cross_results.append((attribute, doc_projco))
                        my_listof_ordereddicts_cross_docs2.append(res_co)

                    except:
                        res_co = ''

        else:
            my_projections = []
            for value in projection_view["data"]:
                my_projections.append(value.get('path'))
            id_doc_to_query = {
                "_id": ObjectId(data_id)
            }

            for projection in my_projections:
                proj_co = {
                    my_projections[my_projections.index(projection)]: 1
                }
                res_co = Data.execute_query(id_doc_to_query).only(proj_co.keys()[0])
                try:
                    my_listof_ordereddicts2.append(res_co)
                except:
                    res_co = ''

            result_data["data"] = parser_processview.processview(nav_id, data_id, projection_view["data"])

        view_data["views"].append(result_data)
    my_node = str(get_node_name(navigation_name2)) + "_" + str(data_id)

    my_listof_ordereddicts_cross_docs_tab.append(my_listof_ordereddicts_cross_docs2)
    my_listof_ordereddicts_tab.append(my_listof_ordereddicts2)
    my_list_of_cross_results_f.append(my_list_of_cross_results)
    my_tab.append(my_node)

    return view_data


def get_node_name(node_id):
    """ Get the name of the node

    Args:
        node_id:

    Returns:

    """
    navigation_name = navigation_api.get_by_id(node_id).name
    index = navigation_name.rfind("#")
    return navigation_name[index+1:]
