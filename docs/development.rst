Development
===========

Running the tests
-----------------

To run the tests, after installing all Python requirements into your
environment::

    bin/test

To view test coverage data, load ``htmlcov/index.html`` in your browser after
running the tests.

To run just a particular test module::

    bin/test tests.core.models.test_product


Compass/Sass
------------

Case Conductor's CSS (located in `static/css`) is generated using `Sass`_ and
the `Compass`_ framework, with the `Susy`_ grid plugin. Sass source files are
located in `sass/`.

The generated CSS is included with Case Conductor, so Sass and Compass are not
needed to run Case Conductor. You only need them if you plan to modify the Sass
sources and re-generate the CSS.

To install the necessary Ruby gems for Compass/Sass development, run
``bin/install-gems``.  Update ``requirements/gems.txt`` if newer gems should be
used.

.. _Sass: http://sass-lang.com
.. _Compass: http://compass-style.org
.. _Susy: http://susy.oddbird.net


Loading sample data
-------------------

A JSON fixture of sample data is provided in ``fixtures/sample_data.json``. To
load this fixture, run ``bin/load-sample-data``.

.. warning::
   Loading the sample data will overwrite existing data in your database. Do
   not load it if you have data in your database that you care about.

The sample data already includes the :ref:`default roles<default-roles>`, so
there is no need to run a separate command to create them.

The sample data also includes four users, one for each default role. Their
usernames are *tester*, *creator*, *manager*, and *admin*. All of them have the
password ``testpw``.


Resetting your database
~~~~~~~~~~~~~~~~~~~~~~~

To drop your database and create a fresh one including only the sample data,
run these commands:

.. note::

   If your shell user doesn't have the MySQL permissions for the first two
   commands, you may need to append e.g. `-uroot` to them.

::

    mysqladmin drop caseconductor
    echo "CREATE DATABASE caseconductor CHARACTER SET utf8" | mysql
    python manage.py syncdb --migrate
    bin/load-sample-data

If you create a superuser during the course of the ``syncdb`` command
(recommended so that you can access the Django admin), the sample data fixture
will not overwrite that superuser.


Regenerating the sample data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sample data fixture is generated using `django-fixture-generator`_ via the
code in ``cc/model/core/fixture_gen.py``,
``cc/model/environments/fixture_gen.py``, ``cc/model/tags/fixture_gen.py``,
``cc/model/library/fixture_gen.py`` and ``cc/model/execution/fixture_gen.py``.

If you've modified one of the above files, you can regenerate the fixture by
running ``bin/regenerate-sample-data``.

.. _django-fixture-generator: http://github.com/alex/django-fixture-generator
