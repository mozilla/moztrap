MozTrap
=======

This is the MozTrap test case management system.  It lives at
https://github.com/mozilla/moztrap/.


Documentation
-------------

For more information about setting up, developing, and using MozTrap, see the
documentation in the `docs/` directory.

To build and view an HTML version of the documentation::

    $ cd docs
    $ pip install sphinx
    $ make html
    $ firefox _build/html/index.html


Related repositories
--------------------

There are `Selenium`_ tests for MozTrap in the `moztrap-tests`_ repository.

MozTrap's Python dependencies are available as sdist tarballs in the
`moztrap-reqs`_ repository, and as an unpacked vendor library in the
`moztrap-vendor-lib`_ repository. These are included as submodules of
this repository, at ``requirements/dist`` and ``requirements/vendor``
respectively.

.. _Selenium: http://seleniumhq.org
.. _moztrap-tests: https://github.com/mozilla/moztrap-tests
.. _moztrap-reqs: https://github.com/mozilla/moztrap-reqs
.. _moztrap-vendor-lib: https://github.com/mozilla/moztrap-vendor-lib
