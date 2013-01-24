REST API
========

These are the REST endpoints available to MozTrap.  These are build using the
`TastyPie`_ package, so please also refer to the TastyPie documentation for more
info.

.. _TastyPie: http://django-tastypie.readthedocs.org/en/latest/resources.html

General
-------

The general format for all rest endpoints is:

.. http:get:: /api/v1/<object_type>/

    Return a list of objects

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/product/?format=json&limit=50

.. http:get:: /api/v1/<object_type/<id>/

    Return a single object

.. http:post:: /api/v1/<object_type>/

    Create one or more items.  **requires** :ref:`API key<api-key>`

.. http:put:: /api/v1/<object_type>/<id>

    Update one item.  **requires** :ref:`API key<api-key>`

.. http:delete:: /api/v1/<object_type>/<id>

    Delete one item.  **requires** :ref:`API key<api-key>`

.. note::

    * POST does not replace the whole list of items, it only creates new ones
    * DELETE on a list is not supported
    * PUT to a list is not supported


Filtering
---------

See each individual :ref:`Object Types<object-types>` for the params it
supports.

Some fields are universal to all requests and :ref:`Object Types<object-types>`:

* **format** (required) The API **always** requires a value of ``json`` for
    this field.
* **limit** (optional) Defaults to 20 items, but can be set higher or lower.
    0 will return all records.


.. note::

    The underscores in query param fields (like ``case__suites``) are **DOUBLE**
    underscores.


.. _object-types:

Supported Object Types
----------------------

.. toctree::
   :maxdepth: 2

   core
   library
   execution
   environments
   tags
   key
