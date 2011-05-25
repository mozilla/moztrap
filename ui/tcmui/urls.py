from django.conf.urls.defaults import patterns, url, include



urlpatterns = patterns(
    "",
    url("^account/", include("tcmui.users.urls")),

    # run tests
    url("^$", "tcmui.testexecution.views.picker", name="runtests"),
    url("^environment/$",
        "tcmui.environments.views.set_environment",
        name="environment"),
    url("^run/(?P<testrun_id>\d+)/$",
        "tcmui.testexecution.views.runtests",
        name="runtests_run"),

    # runtests ajax
    url("^runtests/picker/cycles/(?P<parent_id>\d+)/",
        "tcmui.testexecution.views.picker_cycles",
        name="runtests_picker_cycles"),
    url("^runtests/picker/runs/(?P<parent_id>\d+)/",
        "tcmui.testexecution.views.picker_runs",
        name="runtests_picker_runs"),
    url("^runtests/picker/environments/(?P<parent_id>\d+)/",
        "tcmui.testexecution.views.picker_environments",
        name="runtests_picker_environments"),
    url("^result/(?P<result_id>\d+)/$",
        "tcmui.testexecution.views.result",
        name="result"),

    # manage
    url("^manage/", include("tcmui.manage.urls")),

    # results
    url("^results/", include("tcmui.results.urls")),

    # a sandbox for eric to work on design ideas
    url(r"^wire/design/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "design.html"}),

)
