Environment API
================

Environment
-----------

.. http:get:: /api/v1/environment

    Return a list of environments with all elements and categories.

    :format: (required) The API **always** requires a value of ``json`` for this
        field.
    :elements: (optional) The Element ID to filter on.
    :limit: (optional) Defaults to 20 items, but can be set higher or lower.  0
        will return all records.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/environment/?format=json&elements=5
