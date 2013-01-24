Test Runs API
=============

Test Run
--------

The Test Run (and related) API has some special handling that differs from the
standard APIs.  This is because there is complex logic for submitting results,
and new runs with results can be submitted.

Please consider `MozTrap Connect`_ as a way to submit results for tests.  You
can also check out `MozTrap Connect on github`_.

.. _MozTrap Connect on github: https://github.com/camd/moztrap-connect/
.. _MozTrap Connect: https://moztrap-connect.readthedocs.org/en/latest/index.html


.. http:get:: /api/v1/run
.. http:post:: /api/v1/run

    :productversion: (optional) The ProductVersion ID to filter on.
    :productversion__version: (optional) The ProductVersion ``name`` to filter
        on.  For example, if the Product and Version are ``Firefox 10`` then
        the ``productversion__version`` would be ``10``.
    :productversion__product__name: (optional) The Product ``name`` to filter on.
    :status: (optional) The status of the run.  One of ``active`` or ``draft``.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/run/?format=json&productversion__version=10&case__suites__name=Sweet%20Suite


RunCaseVersions
---------------

.. http:get:: /api/v1/runcaseversion

Filtering
^^^^^^^^^

    :run: The ``id`` of the run
    :run__name: The ``name`` of the run
    :caseversion: The ``id`` of the caseversion
    :caseversion__name: The ``name`` of the caseversion

    .. sourcecode:: http

        GET /api/v1/product/?format=json&run__name=runfoo


Results
-------

.. http:patch:: /api/v1/result

    **Example request**:
    This endpoint is write only.  The submitted result objects should
    be formed like this:

    .. sourcecode:: http

        {
            "objects": [
                {
                    "case": "1",
                    "environment": "23",
                    "run_id": "1",
                    "status": "passed"
                },
                {
                    "case": "14",
                    "comment": "why u no make sense??",
                    "environment": "23",
                    "run_id": "1",
                    "status": "invalidated"
                },
                {
                    "bug": "http://www.deathvalleydogs.com",
                    "case": "326",
                    "comment": "why u no pass?",
                    "environment": "23",
                    "run_id": "1",
                    "status": "failed",
                    "stepnumber": 1
                }
            ]
        }
