"""
URLconf for open web apps

"""
from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "moztrap.view.owa.views",

    # open web apps ----------------------------------------------------------
    url("^manifest.webapp", "manifest", name="owa_manifest"),

)
