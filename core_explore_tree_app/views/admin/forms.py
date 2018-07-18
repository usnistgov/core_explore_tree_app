""" Forms for admin views
"""
from django import forms

from core_main_app.views.admin.commons.upload.forms import UploadForm
from core_main_app.components.template import api as template_api


class UploadQueryOntologyForm(UploadForm):
    """ Form to upload a new Query Ontology file
    """
    templates_manager = forms.ChoiceField(label='', widget=forms.Select(), required=False)

    def __init__(self, *args, **kwargs):
        super(UploadQueryOntologyForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Enter OWL file name'
        self.fields['templates_manager'].label = 'Select the associated template'
        self.fields['templates_manager'].choices = _get_templates_versions()


def _get_templates_versions():
    """ Get templates versions.

    Returns:
        List of templates versions.

    """
    templates = []
    try:
        # display all template, global and from users
        template_list = template_api.get_all()
        for template in template_list:
            templates.append((template.id, template.display_name))
    except Exception:
        pass
    return templates
