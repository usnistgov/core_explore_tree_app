""" Query Ontology model
"""
from django_mongoengine import fields, Document
from mongoengine import errors as mongoengine_errors

from core_main_app.commons.regex import NOT_EMPTY_OR_WHITESPACES
from core_main_app.commons import exceptions
from core_main_app.components.template.models import Template


class QueryOntology(Document):
    """ Ontology of queries to generate the navigation tree
    """
    title = fields.StringField(blank=False, regex=NOT_EMPTY_OR_WHITESPACES)
    status = fields.IntField(default=0, blank=False)  # 0: Uploaded; 1: Active; 2: Blank; -1: Deleted
    last_modification_date = fields.DateTimeField(blank=True)
    content = fields.StringField(blank=False)
    template = fields.ReferenceField(Template, blank=True)

    @staticmethod
    def get_all():
        """ Get all Query Ontology.

        Args:

        Returns:

        """
        return QueryOntology.objects.all()

    @staticmethod
    def get_by_id(query_ontology_id):
        """ Return the object with the given id.

        Args:
            query_ontology_id:

        Returns:
            QueryOntology (obj): QueryOntology object with the given id

        """
        try:
            return QueryOntology.objects.get(pk=str(query_ontology_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)
