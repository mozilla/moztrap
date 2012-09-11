Test Cases and Suites API
=========================

Test Case Version
-----------------

.. http:get:: /api/v1/caseversion

    Return a list of test cases and their versions.

    .. note::

        The underscores in query params (like ``case__suites``) are **DOUBLE**
        underscores.

    :format: (required) The API **always** requires a value of ``json`` for this
        field.
    :productversion: (optional) The ProductVersion ID to filter on.
    :productversion__version: (optional) The ProductVersion ``name`` to filter
        on.  For example, if the Product and Version are ``Firefox 10`` then
        the ``productversion__version`` would be ``10``.
    :case__suites: (optional) The Suite id to filter on.
    :case__suites__name: (optional) The Suite name to filter on.
    :tags__name: (optional) The tag name to filter on.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/caseversion/?format=json&productversion__version=10&case__suites__name=Sweet%20Suite

    **Example response**:

    .. sourcecode:: http

        Content-Type: application/json

        {

            "meta": {
                "limit": 20,
                "next": null,
                "offset": 0,
                "previous": null,
                "total_count": 1
            },
            "objects": [
                {
                    "case": {
                        "id": "13",
                        "resource_uri": "/api/v1/case/13/",
                        "suites": [
                            {
                                "name": "Sweet Suite",
                                "resource_uri": "/api/v1/suite/36/"
                            },
                            {
                                "name": "Sour Suite",
                                "resource_uri": "/api/v1/suite/37/"
                            }
                        ]
                    },
                    "description": "you can pass it. believe.",
                    "environments": [

                        {
                            "elements": [
                                {
                                    "category": {
                                        "id": "2",
                                        "name": "Language",
                                        "resource_uri": "/api/v1/category/2/"
                                    },
                                    "id": "7",
                                    "name": "Mandarin",
                                    "resource_uri": "/api/v1/element/7/"
                                },
                                {
                                    "category": {
                                        "id": "3",
                                        "name": "Operating System",
                                        "resource_uri": "/api/v1/category/3/"
                                    },
                                    "id": "10",
                                    "name": "Windows",
                                    "resource_uri": "/api/v1/element/10/"
                                }
                            ],
                            "id": "46",
                            "resource_uri": "/api/v1/environment/46/"
                        }
                    ],
                    "id": "27",
                    "name": "Can pass test",
                    "productversion": "/api/v1/productversion/2/",
                    "resource_uri": "/api/v1/caseversion/27/",
                    "steps": [
                        {
                            "expected": "it can happen",
                            "instruction": "with enough determination",
                            "resource_uri": "/api/v1/casestep/45/"
                        },
                        {
                            "expected": "of the peaceful warrior",
                            "instruction": "believe in the way",
                            "resource_uri": "/api/v1/casestep/46/"
                        }
                    ],
                    "tags": [
                        {
                            "name": "i swing less",
                            "resource_uri": "/api/v1/tag/87/"
                        },
                        {
                            "name": "i swing more",
                            "resource_uri": "/api/v1/tag/88/"
                        }
                    ]
                }
            ]

        }
