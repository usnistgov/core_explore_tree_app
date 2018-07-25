""" Admin views
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.staticfiles import finders
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.utils.html import escape as html_escape

import core_explore_tree_app.components.query_ontology.api as query_ontology_api
from core_explore_tree_app.commons.enums import QueryOntologyStatus
from core_explore_tree_app.components.query_ontology.models import QueryOntology
from core_explore_tree_app.views.admin.ajax import EditOntologyView, DeleteObjectModalView
from core_explore_tree_app.views.admin.forms import UploadQueryOntologyForm
from core_main_app.commons import exceptions
from core_main_app.utils.file import get_file_http_response
from core_main_app.utils.rendering import admin_render
from core_main_app.views.common.views import read_xsd_file


@staff_member_required
def manage_query_ontology(request):
    """ View that allows ontology management.

    Args:
        request:

    Returns:

    """
    # get all ontologies
    ontologies = query_ontology_api.get_all()

    context = {
        'object_name': 'OWL files',
        'available': [ontology for ontology in ontologies if ontology.status != QueryOntologyStatus.disabled.value],
        'disabled': [ontology for ontology in ontologies if ontology.status == QueryOntologyStatus.disabled.value],
        'status': QueryOntologyStatus.__members__
    }

    assets = {
        "js": [
            {
                "path": 'core_explore_tree_app/admin/js/query_ontology/list/activate.js',
                "is_raw": False
            },
            {
                "path": 'core_explore_tree_app/admin/js/query_ontology/list/disable.js',
                "is_raw": False
            },
            {
                "path": 'core_explore_tree_app/admin/js/query_ontology/list/restore.js',
                "is_raw": False
            },
            EditOntologyView.get_modal_js_path(),
            DeleteObjectModalView.get_modal_js_path(),
        ]
    }

    modals = [
        EditOntologyView.get_modal_html_path(),
        DeleteObjectModalView.get_modal_html_path(),
    ]

    return admin_render(request,
                        'core_explore_tree_app/admin/query_ontology/list.html',
                        assets=assets,
                        context=context,
                        modals=modals)


@staff_member_required
def upload_query_ontology(request):
    """ Upload ontology.

    Args:
        request:

    Returns:

    """
    assets = {
        "js": [
            {
                "path": 'core_main_app/common/js/backtoprevious.js',
                "is_raw": True
            }
        ]
    }

    context = {
        'object_name': 'OWL files',
        'url': reverse("admin:core_explore_tree_app_upload"),
        'redirect_url': reverse("admin:core_explore_tree_app_query_ontology")
    }

    # method is POST
    if request.method == 'POST':
        form = UploadQueryOntologyForm(request.POST,  request.FILES)
        context['upload_form'] = form

        if form.is_valid():
            try:
                _save_query_ontology(request, context)
                return HttpResponseRedirect(reverse("admin:core_explore_tree_app_query_ontology"))
            except Exception, e:
                context['errors'] = html_escape(e.message)
                return admin_render(request,
                                    'core_explore_tree_app/admin/query_ontology/upload.html',
                                    assets=assets,
                                    context=context)
    # method is GET
    else:
        # render the form to upload a template
        context['upload_form'] = UploadQueryOntologyForm()

    return admin_render(request,
                        'core_explore_tree_app/admin/query_ontology/upload.html',
                        assets=assets,
                        context=context)


@staff_member_required
def download_blank_query_ontology(request):
    """ Download ontology.

    Args:
        request:
        pk:

    Returns:

    """
    # open the blank owl file
    owl_file = open(finders.find('core_explore_tree_app/common/owl/blank.owl'))
    # retrieve the content of it
    content = owl_file.read()
    # return the file
    return get_file_http_response(file_content=content,
                                  file_name='blank',
                                  content_type="application/xml",
                                  extension=".owl")


@staff_member_required
def download_query_ontology(request, pk=None):
    """ Download ontology.

    Args:
        request:
        pk:

    Returns:

    """
    # get the ontology
    ontology = query_ontology_api.get_by_id(pk)
    # return the file
    return get_file_http_response(file_content=ontology.content,
                                  file_name=ontology.title,
                                  content_type="application/xml",
                                  extension=".owl")


def _save_query_ontology(request, context):
    """Save a query ontology.

    Args:
        request:
        context:

    Returns:

    """
    # get the schema name
    name = request.POST['name']
    # get the file from the form
    owl_file = request.FILES['upload_file']
    # check the extension file
    if not owl_file.name.endswith('.owl'):
        raise Exception('The extension file must be .owl')
    # retrieve the template id
    template_id = request.POST['templates_manager']
    # read the content of the file
    # FIXME: this method should be renamed to read_file, can't be done in this commit
    owl_data = read_xsd_file(owl_file)
    try:
        owl = QueryOntology(title=name, content=owl_data, template=template_id)
        query_ontology_api.upsert(owl)
    except exceptions.NotUniqueError:
        context['errors'] = html_escape("An Ontology with the same name already exists. Please choose another name.")
    except Exception, e:
        context['errors'] = html_escape(e.message)
