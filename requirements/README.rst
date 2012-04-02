Requirements files
==================

pure.txt
   The pure-Python dependencies of MozTrap. This is the requirements
   file used to generate the bundled vendor library in
   ``requirements/vendor``.

compiled.txt
   The compiled core dependencies of MozTrap.

all.txt
   Includes both ``pure.txt`` and ``compiled.txt``. This is the
   requirements file used by ``bin/install-reqs`` by default.

gems.txt
   Ruby gems necessary to regenerate CSS from modified Sass files; used by
   ``bin/install-gems``.
