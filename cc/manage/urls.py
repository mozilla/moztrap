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
Case Conductor root URLconf.

"""
from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "",

    # testcase ---------------------------------------------------------------
    # manage
    url("^cases/$",
        "cc.manage.views.cases.list",
        name="manage_cases"),

    # ajax details
    url("^cases/_detail/(?P<caseversion_id>\d+)/$",
        "cc.manage.views.cases.details",
        name="manage_case_details"),

    # add
    url("^case/add/$",
        "cc.manage.views.cases.add",
        name="manage_case_add"),

    # add bulk (@@@ wireframe)
    url("^case/add/bulk/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "manage/product/testcase/add_case_bulk.html"},
        name="manage_case_add_bulk"),

    # edit (@@@ wireframe)
    url("^case/id/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "manage/product/testcase/edit_case.html"},
        name="manage_case_edit"),

    # tags -------------------------------------------------------------------
    url(r"^tags/_autocomplete/",
        "cc.manage.views.tags.autocomplete", name="manage_tags_autocomplete"),
)
