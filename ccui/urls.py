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
        url("^debug/", include("ccui.debug.urls")),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT,
                }),
        )
