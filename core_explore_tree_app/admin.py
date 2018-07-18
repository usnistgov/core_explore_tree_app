""" Url router for the administration site
"""
from django.conf.urls import url
from django.contrib import admin

from core_explore_tree_app.views.admin import views as admin_views

admin_urls = [
    url(r'^query-ontology/upload$', admin_views.upload_query_ontology,
        name='core_exploration_tree_app_upload_query_ontology'),
    url(r'^query-ontology', admin_views.manage_query_ontology,
        name='core_exploration_tree_app_query_ontology'),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
