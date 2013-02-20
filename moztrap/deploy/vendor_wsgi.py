"""
Alternative WSGI entry-point that uses requirements/vendor for
dependencies.

"""
import os
import sys

base_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, base_dir)

from moztrap.deploy.paths import add_vendor_lib
add_vendor_lib()

# Set default settings and instantiate application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moztrap.settings.default")

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
