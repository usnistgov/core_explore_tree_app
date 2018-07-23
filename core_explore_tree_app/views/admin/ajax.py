""" explore tree Admin ajax file
"""
import json

from django.http import HttpResponseBadRequest, HttpResponse
from django.urls import reverse_lazy

import core_explore_tree_app.components.query_ontology.api as query_ontology_api
from core_explore_tree_app.commons.enums import QueryOntologyStatus
from core_explore_tree_app.components.query_ontology.models import QueryOntology
from core_explore_tree_app.views.admin.forms import EditOntologyForm
from core_main_app.commons import exceptions
from core_main_app.views.common.ajax import EditObjectModalView, DeleteObjectModalView


def disable_query_ontology(request):
    """ Disable a query ontology

    Args:
        request:

    Returns:

    """
    try:
        query_ontology_api.edit_status(query_ontology_api.get_by_id(request.POST['id']),
                                       QueryOntologyStatus.disabled.value)
        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


def restore_query_ontology(request):
    """ Restore a disabled query ontology

    Args:
        request:

    Returns:

    """
    try:
        query_ontology_api.edit_status(query_ontology_api.get_by_id(request.POST['id']),
                                       QueryOntologyStatus.uploaded.value)
        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


def activate_query_ontology(request):
    """ activate a query ontology

    Args:
        request:

    Returns:

    """
    try:
        query_ontology_api.edit_status(query_ontology_api.get_by_id(request.POST['id']),
                                       QueryOntologyStatus.active.value)
        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


class EditOntologyView(EditObjectModalView):
    form_class = EditOntologyForm
    model = QueryOntology
    success_url = reverse_lazy("admin:core_explore_tree_app_query_ontology")
    success_message = 'Ontology edited with success.'

    def _save(self, form):
        # Save treatment.
        try:
            self.object.title = form.cleaned_data.get('title')
            self.object.template = form.cleaned_data.get('template')
            query_ontology_api.upsert(self.object)
        except exceptions.NotUniqueError:
            form.add_error(None, "An object with the same name already exists. Please choose "
                                 "another name.")
        except Exception, e:
            form.add_error(None, e.message)

    def get_initial(self):
        initial = super(EditOntologyView, self).get_initial()
        initial['template'] = self.object.template.id
        return initial


class DeleteOntologyView(DeleteObjectModalView):
    model = QueryOntology
    success_url = reverse_lazy("admin:core_explore_tree_app_query_ontology")
    success_message = 'Ontology deleted with success.'
    field_for_name = 'title'

    def _delete(self, request, *args, **kwargs):
        # Delete treatment.
        query_ontology_api.delete(self.object)
