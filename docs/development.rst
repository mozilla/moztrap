Development
===========

.. toctree::
   :hidden:

   standards


The :doc:`upgrading` documentation is also applicable to updating your
development checkout of MozTrap.


Community
---------

To connect with MozTrap development, visit the ``#moztrap`` IRC channel at
``irc.mozilla.org``, or see the `Pivotal Tracker backlog`_.

.. _Pivotal Tracker backlog: https://www.pivotaltracker.com/projects/280483


Updating this documentation
---------------------------

MozTrap documentation is hosted on ReadTheDocs.org and is maintained in the
MozTrap repo.  So updating the docs involves forking the repo, changing the
appropriate reStructuredText documents and submitting a pull request.  Then
the team will review them and merge them after any needed adjustments are made.

So here are your steps:

    #. fork the `MozTrap repo`_
    #. make any changes in the ``/docs`` folder using `Sphinx and
       reStructuredText`_ formatting
    #. test that your changes are correctly formatted by installing the python
       Sphinx package (in the repo's ``requirements.txt`` document) by typing
       ``make html`` in that same ``/docs`` folder
    #. load the file: ``/docs/_build/html/index.html`` into your browser
       (it's `Firefox`_, right?) to test your changes
    #. submit your pull request and it will be reviewed shortly
    #. receive a big thanks for helping!!

.. _MozTrap repo: https://github.com/mozilla/moztrap
.. _Sphinx and reStructuredText: http://sphinx-doc.org/rest.html
.. _Firefox: http://www.mozilla.org/en-US/firefox/new/


Coding standards
----------------

See the :doc:`standards` for help writing code that will maintain a consistent
style and quality with the rest of the codebase.


User registration
-----------------

MozTrap's default settings use Django's "console" email backend to avoid
requiring an SMTP server or sending real emails in development/testing mode. So
when registering a new user, pay attention to your runserver console; this is
where the confirmation email text will appear with the link you need to visit
to activate the new account.


Running the tests
-----------------

To run the tests, after installing all Python requirements into your
environment::

    bin/test

To view test coverage data, load ``htmlcov/index.html`` in your browser after
running the tests.

To run just a particular test module, give the dotted path to the module::

    bin/test tests.model.core.models.test_product

Give a dotted path to a package to run all tests within that package, including
in submodules::

    bin/test tests.model.core



Compass/Sass
------------

MozTrap's CSS (located in `static/css`) is generated using `Sass`_ and
the `Compass`_ framework, with the `Susy`_ grid plugin. Sass source files are
located in `sass/`.

The generated CSS is included with MozTrap, so Sass and Compass are not
needed to run MozTrap. You only need them if you plan to modify the Sass
sources and re-generate the CSS.

To install the necessary Ruby gems for Compass/Sass development, run
``bin/install-gems``.  Update ``requirements/gems.txt`` if newer gems should be
used.

While tweaking the sass files, you should run the command line file to update
the CSS as you go.  To do this::

    compass watch

or a workaround to a bug for Mac OS 10.8::

    compass watch --poll


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

    mysqladmin drop moztrap
    echo "CREATE DATABASE moztrap CHARACTER SET utf8" | mysql
    python manage.py syncdb --migrate
    bin/load-sample-data

If you create a superuser during the course of the ``syncdb`` command
(recommended so that you can access the Django admin), the sample data fixture
will not overwrite that superuser.


Regenerating the sample data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sample data fixture is generated using `django-fixture-generator`_ via
the code in ``moztrap/model/core/fixture_gen.py``,
``moztrap/model/environments/fixture_gen.py``,
``moztrap/model/tags/fixture_gen.py``,
``moztrap/model/library/fixture_gen.py`` and
``moztrap/model/execution/fixture_gen.py``.

If you've modified one of the above files, you can regenerate the fixture by
running ``bin/regenerate-sample-data``.

.. _django-fixture-generator: http://github.com/alex/django-fixture-generator


Adding or updating a dependency
-------------------------------

Adding a new dependency (or updating an existing one to a newer version)
involves a few steps, since the requirements files and both submodules (the
requirements tarballs submodule in ``requirements/dist`` and the :ref:`vendor
library` submodule in ``requirements/vendor``) must be updated.


Preparing your checkout
~~~~~~~~~~~~~~~~~~~~~~~

By default, the submodules are both checked out via a read-only anonymous URL,
so that anyone can check them out. In order to push commits to the submodules,
you'll need to switch the push url to use ssh. Make this change as follows::

    cd requirements/dist
    git remote set-url --push origin git@github.com:mozilla/moztrap-reqs

    cd ../vendor
    git remote set-url --push origin git@github.com:mozilla/moztrap-vendor-lib

This assumes that you have permission to push to the primary
``moztrap-reqs`` and ``moztrap-vendor-lib`` repositories. If
instead you have made your own forks of one or both of these repositories,
adjust the above URLs to push to your fork.


Adding the dependency tarball
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assuming the new dependency is a Python package available on `PyPI`_ (for the
sake of this example we'll assume that we want the `2.1.1 version of the
Markdown package`_), from the root of your MozTrap checkout run this
command in order to download the tarball into ``requirements/dist``::

    pip install -d requirements/dist Markdown==2.1.1

This should add the ``Markdown-2.1.1.tar.gz`` file into
``requirements/dist``. We want to add this file and commit the change to the
submodule. First, though, we need to ensure that we are actually committing on
a branch in the submodule, since by default git does not check out submodules
on a branch.

In most cases, you can just check out the ``master`` branch of the submodule
and commit there::

    cd requirements/dist
    git checkout master
    git add Markdown-2.1.1.tar.gz
    # "git rm" the older Markdown tarball, if you're updating
    git commit -m "Add Markdown 2.1.1."
    git push

.. note::

   If you are working on a release branch of MozTrap rather than the master
   branch, you may find that updating the submodule to ``master`` updates the
   version of some dependency to a more recent version, and your branch of
   MozTrap is not prepared for this dependency update. In that case rather than
   updating to the submodule's master branch, you should create a new branch of
   the submodule with a name matching the branch of MozTrap you are working on;
   replace ``git checkout master`` in the above with e.g. ``git branch
   0.8.X``. (If you've already done the ``git checkout master``, go back out to
   the MozTrap repo root and ``git submodule update`` to get back to the pinned
   commit of the submodule, then ``cd requirements/dist`` and ``git branch
   0.8.X``.) If you create your own branch of the submodule, you may need to
   also replace ``git push`` with e.g. ``git push -u origin 0.8.X``).

   Similarly, if you are working on a feature branch, and your feature branch
   requires a newer version of a dependency, it is preferable to make a branch
   of the submodule. The master branch of MozTrap is tied to a specific
   commit of the submodule, so it won't create an immediate problem if you just
   push to the submodule's master branch; but if some other feature on the
   master branch must also update a dependency, there could be a problem if
   everyone is just pushing to the submodule's master branch. (If you are just
   adding a dependency, not changing the version of an existing one, this
   really isn't an issue, as having the extra tarball around won't hurt
   anything for another branch).


Updating the requirements file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your added dependency is a pure-Python dependency (no compiled C
extensions), add an entry to ``requirements/pure.txt`` like
``Markdown==2.1.1``.

If your added dependency does require compilation, add it to
``requirements/compiled.txt`` instead.

If you are just updating the version of an existing dependency, find the
existing requirement line and change the version.


Updating the vendor library
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   This step is only necessary for pure-Python dependencies. Compiled
   dependencies should not be included in the vendor library.

.. note::

   Due to a bug in pip, this step currently must be done within an empty
   ``--no-site-packages`` `virtualenv`_. (Virtualenv 1.7+ automatically creates
   ``--no-site-packages`` envs by default; with an earlier version you must use
   the ``--no-site-packages`` flag).

   If you've correctly created and activated a ``-no-site-packages``
   virtualenv, ``pip freeze`` should show only the ``wsgiref`` package (which
   is part of the Python standard library).

Now, from the root of the MozTrap repo, run::

    bin/generate-vendor-lib
    cd requirements/vendor
    git status

The only changed files shown here should be the new Python files for your added
dependency (or, if upgrading a dependency, possibly some added/modified/removed
files, but nothing outside the one upgraded package).

If that is the case, commit your changes to the master branch (or the branch
you chose earlier) and push using the same steps as shown above for the
``requirements/dist`` submodule.


Pulling it all together
~~~~~~~~~~~~~~~~~~~~~~~

At this point, if you run ``git status`` in the root of the MozTrap
repo, you should see three modifications: a modification to
``requirements/pure.txt`` and ``(new commits)`` in the ``requirements/dist``
and ``requirements/vendor`` submodules (or, if you added a compiled module, a
modification to ``requirements/compiled.txt`` and ``(new commits)`` only in
``requirements/dist``).

Add these changes, commit, push, and you're done!

::

    git add requirements/
    git ci -m "Add Markdown 2.1.1 dependency."
    git push



.. _PyPI: http://pypi.python.org/pypi/
.. _2.1.1 version of the Markdown package: http://pypi.python.org/pypi/Markdown/2.1.1
.. _virtualenv: http://www.virtualenv.org
