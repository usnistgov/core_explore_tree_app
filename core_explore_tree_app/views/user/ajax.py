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
from core_explore_tree_app.utils.dict import *
from core_explore_tree_app.utils.queryNode import queryNode
from core_explore_tree_app.utils.xml.projection import get_projection
from core_main_app.components.data.models import Data
from core_main_app.utils.file import get_file_http_response
from xml_utils.xsd_tree.xsd_tree import XSDTree

leaf_cache = caches['leaf']
branch_cache = caches['branch']
link_cache = caches['link']


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
    xml_document = Data.get_by_id(data_id)
    projection_views = json.loads(navigation_node.options["projection_view"])

    view_data = {
        "header": xml_document.title,
        "type": "leaf",
        "views": [],
        "download": []

    }
    # Initialize parameters in order to download later some information
    # dict of doc_id and queries done of cross documents : {id_doc1: [list of queries1], id_doc2: [list of queries2]}
    dict_id_and_queries_cross_docs = dict()
    # dict of doc_id and queries results for a cross document : {id_doc: [list of queries results]}
    dict_id_and_queryresults_cross_docs = dict()

    # dict of queried parameter and associated result for the queries done on the main doc : { queried parameter: value}
    dict_tags_values_main_doc = dict()

    values_of_items_from_main_doc = []
    list_values_of_items_from_main_doc = []

    # Send the annotation to the processor and collect the data
    for projection_view in projection_views:
        result_data = {
            "title": projection_view["title"],
            "data": None
        }

        # FIXME better handling of x-queries
        # Get info from other doc (without the main queried document)
        if "query" in projection_view.keys():
            doc_projections = []
            # Get the names of the tags tag need to be displayed
            for value in projection_view["data"]:
                doc_projections.append(value.get('path'))

            result_data["data"] = parser_processview.process_cross_query(nav_id,
                                                                         data_id,
                                                                         projection_view["query"],
                                                                         projection_view["data"])
            # Get all the queried documents (without the main queried document)
            queried_docs = parser_processview.ids_docs_to_querys
            for id_doc in queried_docs:
                other_doc_query = {
                    "_id": ObjectId(id_doc)
                }
                # list of queries done on the current document
                query_list = list()
                # list of queries results done on the current document
                result_list = list()

                for projection in doc_projections:
                    # Get the MongoDB query path for the parameter that need to be displayed
                    # eg: query_path = dict_content.a.b.c.d.e
                    query_path = {
                        doc_projections[doc_projections.index(projection)]: 1
                    }
                    # Get the Data corresponding to the id
                    queried_data = Data.execute_query(other_doc_query).only(query_path.keys()[0])
                    # Add the query to the query list for the current doc
                    query_list.append(query_path.keys()[0].replace("dict_content.", ""))
                    try:
                        # Get the result of the query
                        result_query = get_projection(queried_data[0])
                        # Add the result of the query to the result list for the current doc
                        result_list.append(str(result_query))
                    except:
                        pass
                dict_id_and_queries_cross_docs[id_doc] = query_list
                dict_id_and_queryresults_cross_docs[id_doc] = result_list
        # Get info from main doc
        else:
            # list of queries done on the current document (Main doc)
            query_list = list()
            doc_projections = []
            for value in projection_view["data"]:
                doc_projections.append(value.get('path'))

            for projection in doc_projections:
                # Get the MongoDB query path for the parameter that need to be displayed
                # eg: query_path = dict_content.a.b.c.d.e
                query_path = {
                    doc_projections[doc_projections.index(projection)]: 1
                }
                # Add the query to the query list for the current doc (Main doc)
                query_list.append(query_path.keys()[0])
            # Get all results of the queries. type(result_data["data"]) = dict or instance of dict
            result_data["data"] = parser_processview.processview(nav_id, data_id, projection_view["data"])

            i = 0
            for dict_result in result_data["data"]:
                for key in dict_result:
                    # We have only one value as result for the query
                    if "value" in str(key):
                        query_path = query_list[i]  # eg: query_path = a.b.c.d
                        needed_tag = query_path.split(".")  # Get only d (the needed tag)
                        tag = needed_tag[len(needed_tag) - 1]
                        dict_tags_values_main_doc[tag] = dict_result[key]
                    # We have multiple values for this result: all the chemical components
                    # (dict_result[key] is an inclusion of dicts)
                    elif "item" in str(key):
                        # From the inclusion of dict, process the dict into a list and get all the needed values
                        # values_of_items_from_main_doc = list[list[value1 for dict i,value2 for dict 2, ..]]
                        # eg: values_of_items_from_main_doc= [l1,l2]
                        # l1 = [["location", "NIST"], ["Build location X", "59"], "EWI_Build1"]]
                        # l2 = [["location", "NIST"], ["Build location X", "47"], "EWI_Build2"]]
                        get_values_items(dict_result[key], values_of_items_from_main_doc)
                        for list_of_values in values_of_items_from_main_doc:
                            for value in list_of_values:
                                # We have a list :value= [displayed parameter, value]
                                # eg : ["Build location X", "59"]
                                if len(value) == 2:
                                    # list_tag_of_items_from_main_doc.append(value[0])
                                    list_values_of_items_from_main_doc.append(value[1])  # Get the value. eg: 59
                                # We have only one value (last value in the list. eg: EWI_Build1 in l1)
                                else:
                                    list_values_of_items_from_main_doc.append(value)
                i += 1

        view_data["views"].append(result_data)

    # Get the displayed data as an XML format in order to download it later #

    # STEP 1: Build the XML based on initial tags for the crossed documents:

    # Go into the dict of doc_id and queries of cross documents and build the xml for each document
    #  dict_id_and_queries_cross_docs = {id_doc1: [list of queries1], id_doc2: [list of queries2]}
    xml_cross_queries_string = ""
    for key in dict_id_and_queries_cross_docs:  # key = doc_id
        # Get all queries for the current doc_id.
        # eg: query_list = ["a.b.c.d","a.b.c.e","a.b.f.g"]
        query_list = dict_id_and_queries_cross_docs[key]
        # For the doc_id get all the results of the queries done
        # results = ["D","E","G"]
        results = dict_id_and_queryresults_cross_docs[key]
        # Build a xml string for the doc associated to doc_id thanks to the list of queries and the result list
        xml_string = queryNode.tree_to_xml_string(queryNode.aggregate_query(query_list, results))
        xml_object = XSDTree.fromstring(xml_string + "</data>")
        # Add the XML part to create an XML resulting of tag and values of crossed documents
        xml_cross_queries_string += XSDTree.tostring(xml_object, pretty=True)

    # STEP 2: Build the XML for the main document with only the needed tags:
    # Get the Data associated to the main document
    data = Data.get_by_id(data_id)
    # Get the XML content
    file_content = data.xml_content
    xml_main_doc = XSDTree.fromstring(file_content)
    # Transform all the result value into a string to help while testing equality of values with the original XML
    for key in dict_tags_values_main_doc:
        value = dict_tags_values_main_doc[key]
        try:
            dict_tags_values_main_doc[key] = str(value)
        except:
            dict_tags_values_main_doc[key] = u''.join(value).encode('utf-8')
    # Process the XML structure that represents the main document to keep only the needed tags and information
    for child in xml_main_doc.iter():
        # Transform all values into a string
        try:
            text = str(child.text)
        except:
            text = u''.join(child.text).encode('utf-8')
        # If the xml tag is in our dict of tags and values from the main document
        # and its value = dict_tags_values_main_doc[child.tag] we keep the text in the XML structure
        # else we remove the text
        if child.tag in dict_tags_values_main_doc.keys():
            # Fixme  # if text != str(dict_tags_values_main_doc[child.tag]) or dict_tags_values_main_doc[child.tag] not in text: (caution: does not keep all needed values if we replace by this line)
            if text == str(dict_tags_values_main_doc[child.tag]):
                pass
            elif dict_tags_values_main_doc[child.tag] in text:
                pass
            else:
                child.text = ""
        else:
            # If text is in our list of items of the main doc we keep the value and remove it from our list of items
            if text in list_values_of_items_from_main_doc:
                list_values_of_items_from_main_doc.remove(text)
            else:
                display_text = False
                # v = processed name of the tag as appears in the rendered data after clicking a doc of the tree
                # If this name is in our list of items from the main doc we keep the value (text) in the XML tree
                # else we remove this value
                for v in list_values_of_items_from_main_doc:
                    if v in text:
                        display_text = True
                        break
                if not display_text:#==False:
                    child.text = ""

    xml_f_main_doc = xml_main_doc
    # Remove empty leafs of the tree (all child where child.text="")
    while check_empty_nodes(xml_main_doc):
        remove_empty_nodes(xml_f_main_doc)

    # Build the final XML string result of the main doc and the crossed docs
    xml_main_doc = XSDTree.tostring(xml_f_main_doc, pretty="TRUE")
    xml = xml_main_doc + xml_cross_queries_string
    xml_final = "<xml>\n" + xml + "</xml>"
    xml_final = u''.join(xml_final).encode('utf-8')
    xml_final = str(xml_final)
    print dict_tags_values_main_doc
    view_data["download"] = xml_final

    return view_data


def download_displayed_data(request):
    """

    Args:
        request:

    Returns:

    """
    # retrieve all the parameters from the request
    node_id = request.GET.get('current_node', None)
    doc_id = request.GET.get('doc_id', None)
    file_name = request.GET.get('file_name', None)
    load_doc = {}
    if node_id is not None and doc_id is not None:
        node_name = get_node_name(node_id)
        c_id_leaf = str(node_name) + '_' + str(doc_id)
        c_id_link = node_id + '_' + doc_id

        # Get the document from the cache
        # The doc had been reached initially from the tree
        if c_id_leaf in leaf_cache:
            load_doc = leaf_cache.get(c_id_leaf)
        # The doc had been reached initially from a link
        elif c_id_link in link_cache:
            load_doc = link_cache.get(c_id_link)
    return get_file_http_response(file_content=load_doc["download"],
                                  file_name=file_name,
                                  content_type="text/xml",
                                  extension="xml")


def download_source_file(request):
    """

    Args:
        request:

    Returns:

    """
    doc_id = request.GET.get('doc_id', None)
    data = Data.get_by_id(doc_id)
    return get_file_http_response(file_content=data.xml_content,
                                  file_name=data.title,
                                  content_type="text/xml",
                                  extension="xml")


def get_node_name(node_id):
    """ Get the name of the node

    Args:
        node_id:

    Returns:

    """
    navigation_name = navigation_api.get_by_id(node_id).name
    index = navigation_name.rfind("#")
    return navigation_name[index+1:]
