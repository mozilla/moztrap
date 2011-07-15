TCM UI
======

This Django project is the user interface to the new Mozilla/uTest TCM. It
lives at https://github.com/mozilla/tcm/, and is built to speak to the backend
API at https://github.com/mozilla/tcmplatform.

Platform version
----------------

This version of the UI expects to use git commit hash
'197d45a878b0bce3cfcff32e0ffc5bef7f28f3ab' of the platform.


Development
-----------

First, update git submodules (dependency source distribution tarballs are
stored in a git submodule). From the root of this repo, run::

    git submodule init; git submodule update

If you want to run this project in a `virtualenv`_ to isolate it from other
Python projects on your system, create the virtualenv and activate it. Then run
``bin/install-reqs`` to install the dependencies for this project into your
Python environment.

You'll need to create a ``tcmui/settings/local.py`` file with some details of
your local configuration. See ``tcmui/settings/local.sample.py`` for a sample
that can be copied to ``tcmui/settings/local.py`` and modified.

Two settings are required:

``TCM_COMPANY_ID``
    The UI is per-company, and will ignore all data related to other
    companies. This setting should be the (integer) id of the company whose
    data this instance of the UI should manage.

``TCM_NEW_USER_ROLE_ID``
    The (integer) id of the role that all new user registrations should be
    given by default.

The ``create_company`` management command is available to create an initial
company and a default user role. Run ``./manage.py create_company "Company
Name"``; a new company named "Company Name" and two roles, named "Company Name
Tester" and "Company Name Admin" will be created, and the command will output
their IDs, which can then be used for the above two settings.

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

To install the necessary Ruby Gems for Compass/Sass development, run
``bin/install-gems requirements/gems.txt``.  Update
``requirements/gems.txt`` if newer gems should be used.

.. _virtualenv: http://www.virtualenv.org

Running the tests
~~~~~~~~~~~~~~~~~

The UI codebase has an automated test suite. The platform is mocked out in the
test suite, so having the platform running is not a requirement for running the
tests.

To run the tests, after installing all Python requirements into your
environment::

    bin/test

To view test coverage data, load ``coverage/index.html`` in your browser after
running the tests.

To run just a particular test module::

    bin/test tests.core.test_api


Creating sample data
~~~~~~~~~~~~~~~~~~~~

To quickly populate the platform with a small amount of sample data for
development and manual testing, run ``./manage.py create_test_data``. This will
create a user with email address ``tester@example.com`` with the default new
user role and password ``testpw``, as well as several products, a test cycle,
test run, and a couple test cases.

You can optionally pass an argument to the ``create_test_data`` command, the
integer ID of the admin role created by ``create_company`` (above). If given an
admin role ID, ``create_test_data`` will also create an admin user
``admin@example.com`` with that role and password ``testpw``.


Deployment
----------

In addition to the above configuration, in any production deployment this
entire app should be served exclusively over HTTPS (since almost all use of the
site is authenticated, and serving authenticated pages over HTTP invites
session hijacking attacks). Ideally, the non-HTTP URLs should redirect to the
HTTPS version. The ``SESSION_COOKIE_SECURE`` setting should be set to ``True``
in ``settings/local.py`` when the app is being served over HTTPS.

This app also uses the new `staticfiles contrib app`_ in Django 1.3 for
collecting static assets from reusable components into a single directory
for production serving.  Run ``./manage.py collectstatic`` to collect all
static assets into the ``collected-assets`` directory (or whatever
``STATIC_ROOT`` is set to in ``settings/local.py``), and make those
collected assets available by HTTP at the ``STATIC_URL`` setting.

.. _staticfiles contrib app: http://docs.djangoproject.com/en/dev/howto/static-files/
