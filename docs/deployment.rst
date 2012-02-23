Deployment
==========

Django's built-in ``runserver`` is not suitable for a production deployment;
use a WSGI-compatible webserver such as `Apache`_ with `mod_wsgi`_, or
`gunicorn`_. A WSGI application callable is provided in ``cc/deploy/wsgi.py``
in the ``application`` object.

You'll also need to serve the `static assets`_; `Apache`_ or `nginx`_ can do
this.

You'll need a functioning SMTP server for sending user registration
confirmation emails; configure the ``EMAIL_*`` settings in your
``cc/settings/local.py`` to the appropriate values for your server.

In addition to the notes here, you should read through all comments in
``cc/settings/local.sample.py`` and make appropriate adjustments to your
``cc/settings/local.py`` before deploying this app into production.

.. _Apache: http://httpd.apache.org
.. _mod_wsgi: http://modwsgi.org
.. _nginx: http://nginx.org
.. _gunicorn: http://gunicorn.org


Dependencies
------------

For deployment scenarios where pip-installing dependencies into a Python
environment (as ``bin/install-reqs`` does) is not preferred, a pre-installed
vendor library is provided in ``requirements/vendor/lib/python``.  This library
does not include the compiled dependencies listed in
``requirements/compiled.txt``; these must be installed separately via e.g.
system package managers.  The ``site.addsitedir`` function should be used to
add the ``requirements/vendor/lib/python`` directory to sys.path, to ensure
that ``.pth`` files are processed.  A WSGI entry-point script is provided in
``cc/deploy/vendor_wsgi.py`` that makes the necessary ``sys.path`` adjustments,
as well as a version of ``manage.py`` in ``vendor-manage.py``.

If you are using the vendor library and you want to run the Case Conductor
tests, ``bin/test`` won't work as it uses ``manage.py``. Instead run ``python
vendor-manage.py test``.

If you need code coverage metrics (and you have the ``coverage`` module
installed; it isn't included in the vendor library as it has a compiled
extension), use this::

    coverage run vendor-manage.py test
    coverage html
    firefox htmlcov/index.html


Security
--------

In a production deployment this app should be served exclusively over HTTPS,
since almost all use of the site is authenticated, and serving authenticated
pages over HTTP invites session hijacking attacks. The
``SESSION_COOKIE_SECURE`` setting should be set to ``True`` in
``cc/settings/local.py`` when the app is being served over HTTPS.

Run ``python manage.py checksecure`` on your production deployment to check
that your security settings are correct.


Static assets
-------------

This app uses Django's `staticfiles contrib app`_ for collecting static assets
from reusable components into a single directory for production serving.  Run
``./manage.py collectstatic`` to collect all static assets into the
``collected-assets`` directory (or whatever ``STATIC_ROOT`` is set to in
``settings/local.py``), and make those collected assets available by HTTP at
the URL ``STATIC_URL`` is set to.

.. _staticfiles contrib app: http://docs.djangoproject.com/en/dev/howto/static-files/

Database performance tweak
--------------------------

In order to ensure that all database tables are created with the InnoDB storage
engine, Case Conductor's default settings file sets the database driver option
"init_command" to "SET storage_engine=InnoDB". This causes the SET command to
be run on each database connection, which is an unnecessary slowdown once all
tables have been created. Thus, on a production server, you should comment this
option from your ``cc/settings/local.py`` file's ``DATABASES`` setting after
you've run ``python manage.py syncdb --migrate`` to create all tables
(uncomment it before running ``python manage.py syncdb`` or ``python manage.py
migrate`` after an update to the Case Conductor codebase).
