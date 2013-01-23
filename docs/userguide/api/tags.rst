Tags API
=============

Tag
--------

.. http:get:: /api/v1/tag

    Return a list of tags

    .. note::

        Requires an API key in the header.  You must request this API key
        from your MozTrap admin.  It is generated in the User edit page.
        ``username=foo&api_key=bar``

    .. note::

        The underscores in query params (like ``case__suites``) are **DOUBLE**
        underscores.

    :format: (required) The API **always** requires a value of ``json`` for this
        field.
    :name: (optional) The name of the tag.
    :limit: (optional) Defaults to 20 items, but can be set higher or lower.  0
        will return all records.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/tag/?format=json
