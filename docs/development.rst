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
