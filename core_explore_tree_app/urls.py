""" Url router for the Explore tree application
"""

from django.conf.urls import url
from core_explore_tree_app.views.user import views as common_views

urlpatterns = [
    url(r'^$', common_views.index,
        name='core_explore_tree_index'),
]
