""" Url router for the Explore tree application
"""
from django.conf.urls import url, include

from core_explore_tree_app.views.user import ajax as user_ajax
from core_explore_tree_app.views.user import views as user_views

urlpatterns = [
    url(r'^$', user_views.core_explore_tree_index,
        name='core_explore_tree_index'),
    url(r'^load_view/$', user_ajax.load_view,
        name='core_explore_tree_load_view'),
    url(r'^download_source_file/$', user_ajax.download_source_file,
        name='core_explore_tree_app_download_source_file'),
    url(r'^download_displayed_data/$', user_ajax.download_displayed_data,
        name='core_explore_tree_app_download_displayed_data'),
    url(r'^rest/', include('core_explore_tree_app.rest.urls')),
]
