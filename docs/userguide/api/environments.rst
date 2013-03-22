Environment API
===============

Environments do not behave in quite the same way in the API as they do in
the Web UI. In the API, create Categories and their child Elements first,
then create a Profile for which you can create Environments whose elements
must each belong to a separate profile.


Profile
-------

.. http:get:: /api/v1/profile

Filtering
^^^^^^^^^

    :name: The ``name`` of the Profile to filter on.

.. http:get:: /api/v1/profile/<id>
.. http:post:: /api/v1/profile

Required Fields
^^^^^^^^^^^^^^^

    :name: A string Profile name.

.. http:delete:: /api/v1/profile/<id>
.. http:put:: /api/v1/profile/<id>

Category
--------

.. http:get:: /api/v1/category

Filtering
^^^^^^^^^

    :name: The ``name`` of the Category to filter on.

.. http:get:: /api/v1/category/<id>
.. http:post:: /api/v1/category

Required Fields
^^^^^^^^^^^^^^^

    :name: A string Category name.

.. http:delete:: /api/v1/category/<id>
.. http:put:: /api/v1/category/<id>

Element
-------

.. http:get:: /api/v1/element/

Filtering
^^^^^^^^^

    :name: The ``name`` of the Element to filter on.
    :category: The ``id`` of the Category to filter on.
    :category__name: The ``name`` of the Category to filter on.

.. http:get:: /api/v1/element/<id>
.. http:post:: /api/v1/element

Required Fields
^^^^^^^^^^^^^^^

    :name: A string Element name.
    :category: A resource uri to the parent Category.

.. http:delete:: /api/v1/element/<id>
.. http:put:: /api/v1/element/<id>


.. note::

    The Category of an existing Element may not be changed.

Environment
-----------

.. http:get:: /api/v1/environment

Filtering
^^^^^^^^^

    :elements: (optional) The Element ID to filter on.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/environment/?format=json&elements=5

.. http:get:: /api/v1/environment/<id>
.. http:post:: /api/v1/environment

Required Fields
^^^^^^^^^^^^^^^

    :profile: A resource uri to the parent Profile.
    :elements: A list of element resource uri's.

.. note:: Each element must be from a separate category.

.. http:delete:: /api/v1/environment/<id>
.. http:put:: /api/v1/environment/<id>

.. http:patch:: /api/v1/environment

    The `PATCH` command is being overloaded to provide combinatorics
    services to create `environments` out of `elements` contained by
    `categories`.

    To create environments for all of the combinations of elements in
    the listed categories:

    .. sourcecode:: python

        data={
            u'profile': u'/api/v1/profile/1',
            u'categories': [u'/api/v1/category/1', ...]
        }

    You may also do combinatorics with partial sets of elements from
    the categories by using dictionaries with 'include' and 'exclude' keys.

    .. sourcecode:: python

        data={
            u'profile': u'/api/v1/profile/1',
            u'categories': [
                {
                    u'category': u'/api/v1/category/1',
                    u'exclude': [u'/api/v1/element/1']
                },
                {
                    u'category': u'/api/v1/category/2',
                    u'include': [
                        u'/api/v1/element/4',
                        u'/api/v1/element/5'
                    ]
                },
                {
                    u'category': u'/api/v1/category/3'
                }
            ]
        }

    .. note::

        The included or excluded elements must be members of the category
        they accompany. If both include and exclude are sent with the same
        category, exclude will be performed.
