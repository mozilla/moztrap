# A WSGI entry-point that uses requirements/vendor for dependencies.

import os, sys, site

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vendor_lib = os.path.join(base_dir, "requirements", "vendor", "lib", "python")


orig_sys_path = set(sys.path)

# Add project base directory and vendor-lib to sys.path (using site.addsitedir
# for the latter so pth files are processed)
sys.path.append(base_dir)
site.addsitedir(vendor_lib)

# Give new entries precedence over global Python environment
new_sys_path = []
for item in list(sys.path):
    if item not in orig_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path


# Set default settings and instantiate application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ccui.settings.default")

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
