"""WSGI entry-point for MozTrap."""

import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

# Set default settings and instantiate application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moztrap.settings.default")

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

# The following comes from
# https://mana.mozilla.org/wiki/display/websites/How+to+Set+up+New+Relic+for+a+site
try:
    import newrelic.agent
except ImportError:
    newrelic = False

if newrelic:
    newrelic_ini = os.getenv('NEWRELIC_PYTHON_INI_FILE', False)
    if newrelic_ini:
        newrelic.agent.initialize(newrelic_ini)
    else:
        newrelic = False

if newrelic:
    application = newrelic.agent.wsgi_application()(application)
