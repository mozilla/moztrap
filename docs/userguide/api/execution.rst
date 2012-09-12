Test Runs API
=============

Test Run
--------

.. http:get:: /api/v1/run

    Return a list of test runs

    .. note::

        Requires an API key in the header.  You must request this API key
        from your MozTrap admin.  It is generated in the User edit page.
        ``username=foo&api_key=bar``

    .. note::

        The underscores in query params (like ``case__suites``) are **DOUBLE**
        underscores.

    :format: (required) The API **always** requires a value of ``json`` for this
        field.
    :productversion: (optional) The ProductVersion ID to filter on.
    :productversion__version: (optional) The ProductVersion ``name`` to filter
        on.  For example, if the Product and Version are ``Firefox 10`` then
        the ``productversion__version`` would be ``10``.
    :productversion__product__name: (optional) The Product ``name`` to filter on.
    :status: (optional) The status of the run.  One of ``active`` or ``draft``.
    :limit: (optional) Defaults to 20 items, but can be set higher or lower.  0
        will return all records.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/run/?format=json&productversion__version=10&case__suites__name=Sweet%20Suite
