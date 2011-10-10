# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
