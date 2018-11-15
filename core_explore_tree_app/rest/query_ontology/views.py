""" REST views for the Query Ontology API
"""

from django.http import Http404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core_explore_tree_app.commons.enums import QueryOntologyStatus
from core_explore_tree_app.components.query_ontology import api as query_ontology_api
from core_explore_tree_app.rest.query_ontology.serializers import QueryOntologySerializer
from core_main_app.commons import exceptions
from core_main_app.utils.access_control.exceptions import AccessControlError
from core_main_app.utils.decorators import api_staff_member_required
from core_main_app.utils.file import get_file_http_response


class QueryOntologyList(APIView):
    """ List all Query Ontology, or create a new one.
    """
    def get(self, request):
        """ Get all Query Ontology.

        Args:
            request:

        Returns:

        """
        try:
            # Get object
            query_ontology_list = query_ontology_api.get_all()

            # Serialize object
            query_ontology_serializer = QueryOntologySerializer(query_ontology_list, many=True)

            # Return response
            return Response(query_ontology_serializer.data, status=status.HTTP_200_OK)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(api_staff_member_required())
    def post(self, request):
        """ Create Query Ontology

        Args:
            request:

        Returns:

        """
        try:
            # Build serializer
            query_ontology_serializer = QueryOntologySerializer(data=request.data)

            # Validate query ontology
            query_ontology_serializer.is_valid(True)

            # Save query ontology
            query_ontology_serializer.save()

            # Return the serialized query ontology
            return Response(query_ontology_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as validation_exception:
            content = {'message': validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.DoesNotExist:
            content = {'message': 'Query Ontology not found.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QueryOntologyDownload(APIView):
    """ Download content from Query Ontology.
    """
    def get_object(self, request, pk):
        """ Get Query ontology from db

        Args:
            request:
            pk:

        Returns:

        """
        try:
            return query_ontology_api.get_by_id(pk)
        except exceptions.DoesNotExist:
            raise Http404

    @method_decorator(api_staff_member_required())
    def get(self, request, pk):
        """ Download Query Ontology

        Args:
            request:
            pk:

        Returns:

        """
        try:
            # Get object
            query_ontology_object = self.get_object(request, pk)
            return get_file_http_response(query_ontology_object.content,
                                          query_ontology_object.title,
                                          'text/xml', 'owl')
        except Http404:
            content = {'message': 'Query Ontology not found.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QueryOntologyActivate(APIView):
    """ Activate a Query Ontology
    """
    def get_object(self, request, pk):
        """ Get Query ontology from db

        Args:
            request:
            pk:

        Returns:

        """
        try:
            return query_ontology_api.get_by_id(pk)
        except exceptions.DoesNotExist:
            raise Http404

    @method_decorator(api_staff_member_required())
    def patch(self, request, pk):
        """ Activate the given Query Ontology

        Args:
            request:
            pk:

        Returns:

        """
        try:
            # Get object
            query_ontology_object = self.get_object(request, pk)
            # Activate the given Query Ontology
            query_ontology_api.edit_status(query_ontology_object, QueryOntologyStatus.active.value)
            return Response({}, status=status.HTTP_200_OK)
        except Http404:
            content = {'message': 'Query Ontology not found.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        except AccessControlError as ace:
            content = {'message': ace.message}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except Exception as api_exception:
            content = {'message': api_exception.message}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
