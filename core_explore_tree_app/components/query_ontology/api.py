""" Query Ontology  API
"""

from core_explore_tree_app.components.query_ontology.models import QueryOntology


def upsert(query_ontology):
    """ Save or Updates the Query Ontology.

    Args:
        query_ontology:

    Returns:

    """
    return query_ontology.save()


def ontology_delete(ontology):
    """ Delete an Ontology

    Args:
        ontology:

    """
    ontology.delete()


def get_by_id(query_ontology_id):
    """ Return QueryOntology object with the given id.

    Args:
        query_ontology_id:

    Returns: QueryOntology object

    """
    return QueryOntology.get_by_id(query_ontology_id)


def get_all():
    """ Get all the QueryOntology.

    Returns: QueryOntology collection

    """
    return QueryOntology.get_all()
