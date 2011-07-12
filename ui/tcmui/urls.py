from django.conf.urls.defaults import patterns, url, include
from django.conf import settings



urlpatterns = patterns(
    "",
    url("^account/", include("tcmui.users.urls")),

    # run tests
    url("^$", "tcmui.testexecution.views.finder", name="runtests"),
    url("^environment/$",
        "tcmui.environments.views.set_environment",
        name="environment"),
    url("^run/(?P<testrun_id>\d+)/$",
        "tcmui.testexecution.views.runtests",
        name="runtests_run"),

    # runtests ajax
    url("^runtests/_finder/cycles/(?P<parent_id>\d+)/",
        "tcmui.testexecution.views.finder_cycles",
        name="runtests_finder_cycles"),
    url("^runtests/_finder/runs/(?P<parent_id>\d+)/",
        "tcmui.testexecution.views.finder_runs",
        name="runtests_finder_runs"),
    url("^runtests/_finder/environments/(?P<parent_id>\d+)/",
        "tcmui.testexecution.views.finder_environments",
        name="runtests_finder_environments"),
    url("^_result/(?P<result_id>\d+)/$",
        "tcmui.testexecution.views.result",
        name="result"),

    # manage
    url("^manage/", include("tcmui.manage.urls")),

    # results
    url("^results/", include("tcmui.results.urls")),
)

if settings.DEBUG:
    urlpatterns += patterns(
        "",
        url("^debug/", include("tcmui.debug.urls")))
