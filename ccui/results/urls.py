from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "ccui.results.views",
    url("^$", "home", name="results"),

    url(r"^testcycles/$", "testcycles", name="results_testcycles"),
    url(r"^testcycles/_detail/(?P<cycle_id>\d+)/$",
        "testcycle_details",
        name="results_testcycle_details"),
    url(r"^testruns/$", "testruns", name="results_testruns"),
    url(r"^testruns/_detail/(?P<run_id>\d+)/$",
        "testrun_details",
        name="results_testrun_details"),
    url(r"^testcases/$", "testcases", name="results_testcases"),
    url(r"^testcases/_detail/(?P<itc_id>\d+)/$",
        "testcase_details",
        name="results_testcase_details"),
    url(r"^testcase/(?P<itc_id>\d+)/$",
        "testresults",
        name="results_testcase_detail")
)
