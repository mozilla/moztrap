from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "tcmui.results.views",
    url("^$", "home", name="results"),

    url(r"^testcycles/$", "testcycles", name="results_testcycles"),
    url(r"^testruns/$", "testruns", name="results_testruns"),
    url(r"^testcases/$", "testcases", name="results_testcases"),
    url(r"^testcase/(?P<itc_id>\d+)/$",
        "testresults",
        name="results_testcase_detail")
)
