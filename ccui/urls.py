from django.conf.urls.defaults import patterns, url, include
from django.conf import settings



urlpatterns = patterns(
    "",
    url("^account/", include("ccui.users.urls")),

    # run tests
    url("^$", "ccui.testexecution.views.home", name="runtests"),
    url("^environment/(?P<testrun_id>\d+)/$",
        "ccui.environments.views.set_environment",
        name="runtests_environment"),
    url("^run/(?P<testrun_id>\d+)/$",
        "ccui.testexecution.views.runtests",
        name="runtests_run"),

    # runtests ajax
    url("^runtests/_finder/environments/(?P<run_id>\d+)/",
        "ccui.testexecution.views.finder_environments",
        name="runtests_finder_environments"),
    url("^_result/(?P<result_id>\d+)/$",
        "ccui.testexecution.views.result",
        name="result"),

    # manage
    url("^manage/", include("ccui.manage.urls")),

    # results
    url("^results/", include("ccui.results.urls")),
)

if settings.DEBUG:
    urlpatterns += patterns(
        "",
        url("^debug/", include("ccui.debug.urls")))
