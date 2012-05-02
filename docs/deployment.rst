Deployment
==========

Django's built-in ``runserver`` is not suitable for a production deployment;
use a WSGI-compatible webserver such as `Apache`_ with `mod_wsgi`_, or
`gunicorn`_. A WSGI application callable is provided in ``moztrap/deploy/wsgi.py``
in the ``application`` object.

You'll also need to serve the `static assets`_; `Apache`_ or `nginx`_ can do
this.

You'll need a functioning SMTP server for sending user registration
confirmation emails; configure the ``EMAIL_*`` settings and
``DEFAULT_FROM_EMAIL`` in your ``moztrap/settings/local.py`` to the appropriate
values for your server.

The default local-memory `cache backend`_ is not suitable for use with a
production (multi-process) webserver; you'll get CSRF errors on login because
the CSRF token won't be found in the cache. You need an out-of-process cache
backend: memcached or Redis is recommended for production deployment. The
Django file or database cache backends may also work for a small deployment
that is not performance-sensitive. Configure the ``CACHE_BACKENDS`` setting in
``moztrap/settings/local.py`` for the cache backend you want to use.

In addition to the notes here, you should read through all comments in
``moztrap/settings/local.sample.py`` and make appropriate adjustments to your
``moztrap/settings/local.py`` before deploying this app into production.

.. _Apache: http://httpd.apache.org
.. _mod_wsgi: http://modwsgi.org
.. _nginx: http://nginx.org
.. _gunicorn: http://gunicorn.org
.. _cache backend: http://docs.djangoproject.com/en/dev/topics/cache/



Logins
------

By default all access to the site requires authentication. If the
``ALLOW_ANONYMOUS_ACCESS`` setting is set to ``True`` in
``moztrap/settings/local.py``, anonymous users will be able to read-only browse the
management and test-results pages (but will not be able to submit test results
or modify anything).

By default MozTrap uses `BrowserID`_ for all logins, but it also
supports conventional username/password logins. To switch to username/password
logins, just set ``USE_BROWSERID`` to ``False`` in ``moztrap/settings/local.py``.

If using BrowserID (the default), you need to make sure that your ``SITE_URL``
is set correctly in ``moztrap/settings/local.py``, or BrowserID logins will not
work.

.. _BrowserID: http://browserid.org


.. _vendor library:

Vendor library
--------------

For deployment scenarios where pip-installing dependencies into a Python
environment (as ``bin/install-reqs`` does) is not preferred, a pre-installed
vendor library is provided in ``requirements/vendor/lib/python``.  This library
does not include the compiled dependencies listed in
``requirements/compiled.txt``; these must be installed separately via e.g.
system package managers.  The ``site.addsitedir`` function should be used to
add the ``requirements/vendor/lib/python`` directory to sys.path, to ensure
that ``.pth`` files are processed.  A WSGI entry-point script is provided in
``moztrap/deploy/vendor_wsgi.py`` that makes the necessary ``sys.path`` adjustments,
as well as a version of ``manage.py`` in ``vendor-manage.py``.

If you are using the vendor library and you want to run the MozTrap
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
``moztrap/settings/local.py`` when the app is being served over HTTPS.

Run ``python manage.py checksecure`` on your production deployment to check
that your security settings are correct.


Static assets
-------------

This app uses Django's `staticfiles contrib app`_ for collecting static assets
from reusable components into a single directory for production serving, and
uses `django-compressor`_ to compress and minify them. Follow these steps to
deploy the static assets into production:

1. Ensure that ``COMPRESS_ENABLED`` and ``COMPRESS_OFFLINE`` are both
   uncommented and set to ``True`` in ``moztrap/settings/local.py``.

2. Run ``python manage.py collectstatic`` to collect all static assets into the
   ``collected-assets`` directory (or whatever ``STATIC_ROOT`` is set to in
   ``moztrap/settings/local.py``).

3. Run ``python manage.py compress`` to minify and concatenate static assets.

4. Make the entire resulting contents of ``STATIC_ROOT`` available over HTTP at
   the URL ``STATIC_URL`` is set to.

If deploying to multiple static assets servers, probably steps 1-3 should be
run once on a deployment or build server, and then the contents of
``STATIC_ROOT`` copied to each web server.

.. _staticfiles contrib app: http://docs.djangoproject.com/en/dev/howto/static-files/
.. _django-compressor: http://django_compressor.readthedocs.org/en/latest/index.html


.. _database-performance-tweak:

Database performance tweak
--------------------------

In order to ensure that all database tables are created with the InnoDB
storage engine, MozTrap's default settings file sets the database
driver option "init_command" to "SET storage_engine=InnoDB".  This causes
the SET command to be run on each database connection, which is an
unnecessary slowdown once all tables have been created.  Thus, on a
production server, you should comment this option from your
``moztrap/settings/local.py`` file's ``DATABASES`` setting after you've run
``python manage.py syncdb --migrate`` to create all tables (uncomment it
before running ``python manage.py syncdb`` or ``python manage.py migrate``
after an update to the MozTrap codebase, or before trying to run the
tests).
