Core Explore Tree App
=====================

Exploration tree feature for the curator core project.


Configuration
=============

1. Add "core_explore_tree_app" to your INSTALLED_APPS setting like this
-----------------------------------------------------------------------

.. code:: python

    INSTALLED_APPS = [
        ...
        "core_explore_tree_app",
    ]

2. Include the core_explore_tree_app URLconf in your project urls.py like this
------------------------------------------------------------------------------

.. code:: python

    url(r'^', include("core_explore_tree_app.urls")),
