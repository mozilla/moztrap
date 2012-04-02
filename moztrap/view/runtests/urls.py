"""
URLconf for running tests

"""
from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "cc.view.runtests.views",

    url(r"^$", "select", name="runtests"),
    url(r"^environment/(?P<run_id>\d+)/$",
        "set_environment",
        name="runtests_environment"),
    url(r"^run/(?P<run_id>\d+)/env/(?P<env_id>\d+)/$",
        "run",
        name="runtests_run"),

)
