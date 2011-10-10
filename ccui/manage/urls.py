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
    "ccui.manage.views",
    url("^$", "home", name="manage"),

    # products
    url("^products/$", "products", name="manage_products"),
    url("^product/add/$", "add_product", name="manage_product_add"),
    url("^product/(?P<product_id>\d+)/$", "edit_product", name="manage_product_edit"),

    # test cycles
    url("^testcycles/$", "testcycles", name="manage_testcycles"),
    url("^testcycles/_detail/(?P<cycle_id>\d+)/$",
        "testcycle_details",
        name="manage_testcycle_details"),
    url("^testcycle/add/$", "add_testcycle", name="manage_testcycle_add"),
    url("^testcycle/(?P<cycle_id>\d+)/$", "edit_testcycle", name="manage_testcycle_edit"),

    # test runs
    url("^testruns/$", "testruns", name="manage_testruns"),
    url("^testruns/_detail/(?P<run_id>\d+)/$",
        "testrun_details",
        name="manage_testrun_details"),
    url("^testrun/add/$", "add_testrun", name="manage_testrun_add"),
    url("^testrun/(?P<run_id>\d+)/$", "edit_testrun", name="manage_testrun_edit"),

    # test suites
    url("^testsuites/$", "testsuites", name="manage_testsuites"),
    url("^testsuites/_detail/(?P<suite_id>\d+)/$",
        "testsuite_details",
        name="manage_testsuite_details"),
    url("^testsuite/add/$", "add_testsuite", name="manage_testsuite_add"),
    url("^testsuite/(?P<suite_id>\d+)/$", "edit_testsuite", name="manage_testsuite_edit"),

    # test cases
    url("^testcases/$", "testcases", name="manage_testcases"),
    url("^testcases/_detail/(?P<case_id>\d+)/$",
        "testcase_details",
        name="manage_testcase_details"),
    url("^testcase/add/$", "add_testcase", name="manage_testcase_add"),
    url("^testcase/add/bulk/$", "add_testcase_bulk", name="manage_testcase_add_bulk"),
    url("^testcase/(?P<case_id>\d+)/$", "edit_testcase", name="manage_testcase_edit"),

    # environment profiles
    url(r"^environments/$", "environment_profiles", name="manage_environments"),
    url(r"^environment/add/$", "add_environment_profile", name="manage_environment_add"),
    url(r"^environment/edit/(?P<profile_id>\d+)/$", "edit_environment_profile", name="manage_environment_edit"),
    url(r"^environment/_elements/", "autocomplete_env_elements", name="manage_environment_autocomplete_elements"),

    # environment narrowing
    url(r"^(?P<object_type>product|testcycle|testrun|testsuite|testcase)/"
        "(?P<object_id>\d+)/environments/$",
        "narrow_environments",
        name="manage_narrow_environments"),

    # users
    url(r"^users/$", "users", name="manage_users"),
    url(r"^users/add/$", "add_user", name="manage_user_add"),
    url(r"^users/edit/(?P<user_id>\d+)/$", "edit_user", name="manage_user_edit"),

    # tags
    url(r"^tags/$", "tags", name="manage_tags"),
    url(r"^tags/_autocomplete/", "tags_autocomplete", name="manage_tags_autocomplete"),

)
