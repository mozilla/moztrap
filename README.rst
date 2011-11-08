Case Conductor is a Test Case Management system.
Copyright (C) 2011 uTest Inc.

This file is part of Case Conductor.

Case Conductor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Case Conductor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.

Case Conductor UI
=================

This Django project is the user interface to the Case Conductor test case
management system.  It lives at
https://github.com/mozilla/caseconductor-ui/, and is built to speak via HTTP
API to the platform at https://github.com/mozilla/caseconductor-platform.


Platform
--------

This version of the UI expects to use git commit hash
'be67224de3336790deb23fceb420a8feb062c40c' of the platform.  A pre-built WAR
file of this version of the platform is provided at ``platform/tcm.war``. 
The database scripts required to set up an initial platform database are in
``platform/db_scripts``, and ``platform/reset-mysql.sh`` automates setting
up the database.  (See the platform README at ``platform/README.rst``).


Development
-----------

The Case Conductor UI requires Python 2.6 or 2.7.

First, update git submodules (dependency source distribution tarballs are
stored in a git submodule). From the root of this repo, run::

    git submodule init; git submodule update

If you want to run this project in a `virtualenv`_ to isolate it from other
Python projects on your system, create the virtualenv and activate it. Then run
``ui/bin/install-reqs`` to install the dependencies for this project into your
Python environment.

You'll need to create a ``ccui/settings/local.py`` file with some details of
your local configuration. See ``ccui/settings/local.sample.py`` for a sample
that can be copied to ``ccui/settings/local.py`` and modified.

Two settings are required:

``CC_COMPANY_ID``
    The UI is per-company, and will ignore all data related to other
    companies. This setting should be the (integer) id of the company whose
    data this instance of the UI should manage.

``CC_NEW_USER_ROLE_ID``
    The (integer) id of the role that all new user registrations should be
    given by default.

The ``create_company`` management command is available to create an initial
company and default user roles.  Run ``./manage.py create_company "Company
Name"``; a new company named "Company Name" and three roles, named "Tester",
"Test Manager", and "Admin" will be created, and the command will output
their IDs, which can then be used for the above two settings.

Several other settings have reasonable defaults, but may need to be modified:

``CC_API_BASE``
    The base URL for the platform API. Defaults to
    ``"http://localhost:8080/tcm/services/v2/rest/"``

``CC_ADMIN_USER``
    The UI generally uses the privileges of the logged-in user for all API
    calls, but requires admin privileges on the platform API for certain
    operations, such as creating new users and assigning them their default
    role. This should be the email address of the admin credentials to use;
    defaults to ``"admin@utest.com"``.

``CC_ADMIN_PASS``
    Password for ``CC_ADMIN_USER``. Defaults to ``"admin"``.

Once this configuration is done, you should be able to run ``./manage.py
runserver`` and access the UI in your browser at ``http://localhost:8000``.

All Compass/Sass files are pre-compiled to CSS, so no gems are development, run
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

Django's ``runserver`` is not suitable for a production deployment; use a
WSGI-compatible webserver such as `Apache`_ with `mod_wsgi`_, or
`gunicorn`_. You'll also need to serve the static assets; `Apache`_ or `nginx`_
can do this.

For deployment scenarios where pip-installing dependencies into a Python
environment (as ``bin/install-reqs`` does) is not preferred, a pre-installed
vendor library is also provided in ``requirements/vendor/lib/python``. The
``site.addsitedir`` function should be used to add this directory to sys.path,
to ensure that ``.pth`` files are processed. A WSGI entry-point script is
provided in ``deploy/vendor.wsgi`` that does all the necessary ``sys.path``
adjustments.

In addition to the above configuration, in any production deployment this
entire app should be served exclusively over HTTPS (since almost all use of the
site is authenticated, and serving authenticated pages over HTTP invites
session hijacking attacks). Ideally, the non-HTTP URLs should redirect to the
HTTPS version. The ``SESSION_COOKIE_SECURE`` setting should be set to ``True``
in ``ccui/settings/local.py`` when the app is being served over HTTPS. You can
run "python manage.py checksecure" on your production deployment to check that
your security settings are correct.

Case Conductor UI stores user session information in the cache. For local
development the default cache backend is the "local memory" backend. Since many
production webservers are multi-process, this cache backend is unsuitable for
production use. Preferably, `memcached`_ should be used as the production cache
backend. Alternately, to reduce infrastructure dependencies for very small
installations, user sessions can be stored in a SQLite database. Examples of
both of these configurations can be found in the sample local-settings file at
``ccui/settings/local.sample.py``.

This app also uses the new `staticfiles contrib app`_ in Django 1.3 for
collecting static assets from reusable components into a single directory
for production serving.  Run ``./manage.py collectstatic`` to collect all
static assets into the ``collected-assets`` directory (or whatever
``STATIC_ROOT`` is set to in ``settings/local.py``), and make those
collected assets available by HTTP at the ``STATIC_URL`` setting.

.. _staticfiles contrib app: http://docs.djangoproject.com/en/dev/howto/static-files/
.. _memcached: http://memcached.org
.. _Apache: http://httpd.apache.org
.. _nginx: http://nginx.org
.. _gunicorn: http://gunicorn.org/
