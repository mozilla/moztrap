# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
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
    # url(r"^cases/$",
    #     "runcaseversions.views.runcaseversions_list",
    #     name="results_runcaseversions"),

    # ajax detail
    # url(r"^cases/_detail/(?P<rcv_id>\d+)/$",
    #     "runcaseversions.views.runcaseversion_details",
    #     name="results_runcaseversion_details"),

    # results ----------------------------------------------------------------

    # list
    # url(r"^case/(?P<rcv_id>\d+)/$",
    #     "results.views.results_list",
    #     name="results_results")
)
