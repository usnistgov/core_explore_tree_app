import json

from core_explore_tree_app.components.data import api as data_explore_tree_api
from core_explore_tree_app.utils.xml.projection import get_projection
from core_main_app.components.data.models import Data


def _is_advanced_filter(str_filter):
    """ Helper able to determine if a filter is advanced or not

    Args:
         str_filter
    Return:
    """
    try:
        json_filter = json.loads(str_filter)

        expected_keys = {"documents", "query"}
        return len(expected_keys.difference(json_filter.keys())) == 0
    except Exception as exc:
        return False


def execute_query(template_id, filters=list(), projection=None):
    """
    Args:
        template_id:
        filters:
        projection:

    Return:
    """
    # Will be returned at the end
    data_list_result = []

    # Get all data from the given template
    data_id_list = {data.id for data in data_explore_tree_api.get_all_by_list_template([template_id])}

    # Parsing filters if present
    for _filter in filters:
        # Extracted correct documents
        filter_result = []

        try:
            # Loads filter and projection
            json_filter = json.loads(_filter)
            json_projection = json.loads(projection)
        except Exception, e:
            print e.message

        if _is_advanced_filter(_filter):
            json_filter = json.loads(_filter)
            # Get matching document
            #   list possible values of the right hand side
            #   match resulted documents
            documents_field = json_filter["documents"].values()[0]

            values = get_filter_values(documents_field)
            matching_documents = get_matching_document(template_id,
                                                       json_filter["documents"].keys()[0],
                                                       values,
                                                       json_filter["query"])

            for doc in matching_documents:
                doc_cross_query = {json_filter["documents"].values()[0]: get_projection(doc)}
                filter_result += Data.execute_query(doc_cross_query).only(json_projection.keys()[0])
        else:
            filter_result = Data.execute_query(json_filter).only(json_projection.keys()[0])

        filter_id = {document.id for document in filter_result}
        data_id_list = data_id_list.intersection(filter_id)

        data_list_result = [doc for doc in filter_result if doc.id in data_id_list]

    return data_list_result


def get_filter_values(field):
    """ Get matching values for a given field

    Args:
        field:
    Return:
    """
    query = {field: {"$exists": True}}
    documents = Data.execute_query(query).only(field)
    return {get_projection(doc) for doc in documents}


def get_matching_document(template_id, field, values, query):
    """ Get matching document

    Args:
        template_id:
        field:
        values:
        query:

    Return:
    """
    document_set = []
    document_projection = {field: 1}

    for value in values:
        tmp_query = [
            json.dumps(query),
            json.dumps({field: value})
        ]

        document_set += execute_query(template_id, tmp_query, json.dumps(document_projection))

    return document_set


