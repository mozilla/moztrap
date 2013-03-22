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

    **limit** (optional) Defaults to 20 items, but can be set higher or lower.
    0 will return all records, but may run afoul of
    **Example request**:

    .. sourcecode:: http

        GET /api/v1/product/?format=json&limit=50

.. http:get:: /api/v1/<object_type>/<id>/

    Return a single object

.. https:post:: /api/v1/<object_type>/

    Create one or more items.

    **requires** :ref:`API key<api-key>`
    **requires** :ref:`username`

    If sending the fields as data, the data must be sent as json, with
    Content-Type application/json in the headers.

.. https:put:: /api/v1/<object_type>/<id>

    Update one item.
    **requires** :ref:`API key<api-key>`
    **requires** :ref:`username`

.. https:delete:: /api/v1/<object_type>/<id>

    Delete one item.
    **requires** :ref:`API key<api-key>`
    **requires** :ref:`username`

.. note::

    * POST does not replace the whole list of items, it only creates new ones
    * DELETE on a list is not supported
    * PUT to a list is not supported
    * commands that make changes may need to be sent to https, not http.


Query Parameters
----------------

* See each individual :ref:`Object Types<object-types>` for the params it
  supports.
* See `TastyPie Filtering`_ for more info on query parameters.

.. _TastyPie Filtering: http://django-tastypie.readthedocs.org/en/latest/resources.html#basic-filtering


Some fields are universal to all requests and :ref:`Object Types<object-types>`:

* **format** (required) The API **always** requires a value of ``json`` for
    this field.


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
