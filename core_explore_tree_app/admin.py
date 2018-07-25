""" Url router for the administration site
"""
from django.conf.urls import url
from django.contrib import admin

from core_explore_tree_app.views.admin import views as admin_views
from core_explore_tree_app.views.admin import ajax as admin_ajax


admin_urls = [
    url(r'^query-ontology/upload$', admin_views.upload_query_ontology,
        name='core_explore_tree_app_upload'),
    url(r'^query-ontology/download/$', admin_views.download_blank_query_ontology,
        name='core_explore_tree_app_download_blank'),
    url(r'^query-ontology/download/(?P<pk>\w+)/$', admin_views.download_query_ontology,
        name='core_explore_tree_app_download'),
    url(r'^query-ontology/disable$', admin_ajax.disable_query_ontology,
        name='core_explore_tree_app_disable'),
    url(r'^query-ontology/activate$', admin_ajax.activate_query_ontology,
        name='core_explore_tree_app_activate'),
    url(r'^query-ontology/restore$', admin_ajax.restore_query_ontology,
        name='core_explore_tree_app_restore'),
    url(r'^query-ontology/(?P<pk>[\w-]+)/edit/$', admin_ajax.EditOntologyView.as_view(),
        name='core_explore_tree_app_edit'),
    url(r'^query-ontology/(?P<pk>[\w-]+)/delete/$', admin_ajax.DeleteOntologyView.as_view(),
        name='core_explore_tree_app_delete'),
    url(r'^query-ontology/$', admin_views.manage_query_ontology,
        name='core_explore_tree_app_query_ontology'),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
