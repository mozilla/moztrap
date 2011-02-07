TCM UI
======

This Django project is the user interface to the new Mozilla/uTest TCM. It
lives at https://github.com/mozilla/tcm/, and is built to speak to the backend
API at https://github.com/mozilla/tcmplatform.

Development
-----------

First, update git submodules (dependency source distribution tarballs are
stored in a git submodule). From the root of this repo, run::

    git submodule init; git submodule update

If you want to run this project in a `virtualenv`_ to isolate it from other
Python projects on your system, create the virtualenv and activate it. Then run
``bin/install-reqs`` to install the dependencies for this project into your
Python environment.

You'll need to create a ``tcmui/settings_local.py`` file with some details of
your local configuration. Two settings are required:

``TCM_COMPANY_ID``
    The UI is per-company, and will ignore all data related to other
    companies. This setting should be the (integer) id of the company whose
    data this instance of the UI should manage.

``TCM_NEW_USER_ROLE_ID``
    The (integer) id of the role that all new user registrations should be
    given by default.

Several other settings have reasonable defaults, but may need to be modified:

``TCM_API_BASE``
    The base URL for the platform API. Defaults to
    ``"http://localhost:8080/tcm/services/v2/rest/"``

``TCM_ADMIN_USER``
    The UI generally uses the privileges of the logged-in user for all API
    calls, but requires admin privileges on the platform API for certain
    operations, such as creating new users and assigning them their default
    role. This should be the email address of the admin credentials to use;
    defaults to ``"admin@utest.com"``.

``TCM_ADMIN_PASS``
    Password for ``TCM_ADMIN_USER``. Defaults to ``"admin"``.

Once this configuration is done, you should be able to run ``./manage.py
runserver`` and access the UI in your browser at ``http://localhost:8000``.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv
