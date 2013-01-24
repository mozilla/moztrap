.. _api-key:

API Keys
========

API Keys are generated on the ``Manage | Users`` page for a user.  Only an
:ref:`Admin<admin-role>` can create an API Key for a user.

The API key is passed on the query string for an API like this::

    ``POST /api/v1/product?username=camd&api_key=abc123``

