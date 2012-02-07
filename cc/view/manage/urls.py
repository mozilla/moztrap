# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
URLconf for management pages.

"""
from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "",

    # testcase ---------------------------------------------------------------
    # manage
    url(r"^cases/$",
        "cc.view.manage.cases.views.cases_list",
        name="manage_cases"),

    # ajax details
    url(r"^cases/_detail/(?P<caseversion_id>\d+)/$",
        "cc.view.manage.cases.views.case_details",
        name="manage_case_details"),

    # add
    url(r"^case/add/$",
        "cc.view.manage.cases.views.case_add",
        name="manage_case_add"),

    # add bulk
    url(r"^case/add/bulk/$",
        "cc.view.manage.cases.views.case_add_bulk",
        name="manage_case_add_bulk"),

    # edit
    url(r"^case/version/(?P<caseversion_id>\d+)/$",
        "cc.view.manage.cases.views.caseversion_edit",
        name="manage_caseversion_edit"),

    # new version
    url(r"^case/version/(?P<caseversion_id>\d+)/clone/$",
        "cc.view.manage.cases.views.caseversion_clone",
        name="manage_caseversion_clone"),

    # tags -------------------------------------------------------------------
    url(r"^tags/_autocomplete/",
        "cc.view.manage.tags.views.tag_autocomplete",
        name="manage_tags_autocomplete"),
)
