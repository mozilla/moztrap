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

Case Conductor
==============

This is the Case Conductor test case management system.  It lives at
https://github.com/mozilla/caseconductor/.


Development
-----------

Case Conductor requires Python 2.6 or 2.7.

First, update git submodules (dependency source distribution tarballs are
stored in a git submodule). From the root of this repo, run::

    git submodule init; git submodule update

If you want to run this project in a `virtualenv`_ to isolate it from other
Python projects on your system, create the virtualenv and activate it. Then run
``ui/bin/install-reqs`` to install the dependencies for this project into your
Python environment.

You may need to create a ``ccui/settings/local.py`` file with some details of
your local database and other configuration. See
``ccui/settings/local.sample.py`` for a sample that can be copied to
``ccui/settings/local.py`` and modified as needed.

Once this configuration is done, you should be able to run ``./manage.py syncdb
--migrate`` to install the database tables, ``./manage.py runserver`` to run
the local development server, and then access the test case manager in your
browser at ``http://localhost:8000``.

To install the necessary Ruby gems for Compass/Sass development (only
necessary if you plan to modify Sass files and re-generate CSS), run
``bin/install-gems``.  Update ``requirements/gems.txt`` if newer gems should
be used.

.. _virtualenv: http://www.virtualenv.org

Running the tests
~~~~~~~~~~~~~~~~~

To run the tests, after installing all Python requirements into your
environment::

    bin/test

To view test coverage data, load ``htmlcov/index.html`` in your browser after
running the tests.

To run just a particular test module::

    bin/test tests.core.models.test_product


Deployment
----------

Django's ``runserver`` is not suitable for a production deployment; use a
WSGI-compatible webserver such as `Apache`_ with `mod_wsgi`_, or
`gunicorn`_. You'll also need to serve the static assets; `Apache`_ or `nginx`_
can do this.

For deployment scenarios where pip-installing dependencies into a Python
environment (as ``bin/install-reqs`` does) is not preferred, a pre-installed
vendor library is also provided in ``requirements/vendor/lib/python``.  This
library does not include the compiled dependencies listed in
``requirements/compiled.txt``; these must be installed separately via e.g. 
system package managers.  The ``site.addsitedir`` function should be used to
add this directory to sys.path, to ensure that ``.pth`` files are processed. 
A WSGI entry-point script is provided in ``deploy/vendor.wsgi`` that does
all the necessary ``sys.path`` adjustments, as well as a version of
``manage.py`` in ``vendor-manage.py``.

In any production deployment this entire app should be served exclusively over
HTTPS (since almost all use of the site is authenticated, and serving
authenticated pages over HTTP invites session hijacking attacks). Ideally, the
non-HTTP URLs should redirect to the HTTPS version. The
``SESSION_COOKIE_SECURE`` setting should be set to ``True`` in
``ccui/settings/local.py`` when the app is being served over HTTPS. You can run
"python manage.py checksecure" on your production deployment to check that your
security settings are correct.

This app also uses the new `staticfiles contrib app`_ in Django 1.3 for
collecting static assets from reusable components into a single directory
for production serving.  Run ``./manage.py collectstatic`` to collect all
static assets into the ``collected-assets`` directory (or whatever
``STATIC_ROOT`` is set to in ``settings/local.py``), and make those
collected assets available by HTTP at the ``STATIC_URL`` setting.

.. _staticfiles contrib app: http://docs.djangoproject.com/en/dev/howto/static-files/
.. _Apache: http://httpd.apache.org
.. _nginx: http://nginx.org
.. _gunicorn: http://gunicorn.org/
