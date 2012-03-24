"""
URLconf for browse-results pages.

"""
from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "cc.view.results",

    url("^$", "views.home", name="results"),

    # runs ------------------------------------------------------------------

    # list
    url(r"^runs/$",
        "runs.views.runs_list",
        name="results_runs"),

    # ajax detail
    url(r"^runs/_detail/(?P<run_id>\d+)/$",
        "runs.views.run_details",
        name="results_run_details"),

    # runcaseversions --------------------------------------------------------

    # list
    url(r"^cases/$",
        "runcaseversions.views.runcaseversions_list",
        name="results_runcaseversions"),

    # ajax detail
    url(r"^cases/_detail/(?P<rcv_id>\d+)/$",
        "runcaseversions.views.runcaseversion_details",
        name="results_runcaseversion_details"),

    # results ----------------------------------------------------------------

    # list
    url(r"^case/(?P<rcv_id>\d+)/$",
        "results.views.results_list",
        name="results_results")
)
