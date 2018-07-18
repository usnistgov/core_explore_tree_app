""" Navigation model
"""
from django_mongoengine import Document, fields
from mongoengine import errors as mongoengine_errors

from core_main_app.commons import exceptions


class Navigation(Document):
    """ Data structure to handle the navigation tree
    """
    name = fields.StringField(blank=True)
    parent = fields.StringField(blank=True)
    children = fields.ListField(blank=True)
    options = fields.DictField(blank=True)

    @staticmethod
    def get_all():
        """ Get all Navigation.

        Args:

        Returns:

        """
        return Navigation.objects.all()

    @staticmethod
    def get_by_id(navigation_id):
        """ Return the object with the given id.

        Args:
            navigation_id:

        Returns:
            Navigation(obj): Navigation object with the given id

        """
        try:
            return Navigation.objects.get(pk=str(navigation_id))
        except mongoengine_errors.DoesNotExist as e:
            raise exceptions.DoesNotExist(e.message)
        except Exception as ex:
            raise exceptions.ModelError(ex.message)
