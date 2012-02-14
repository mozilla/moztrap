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
    "cc.view.manage",

    url(r"^$", "views.home", name="manage"),

    # user ------------------------------------------------------------------
    # manage
    url(r"^users/$",
        "users.views.users_list",
        name="manage_users"),

    # add
    url(r"^user/add/$",
        "users.views.user_add",
        name="manage_user_add"),

    # edit
    url(r"^user/(?P<user_id>\d+)/$",
        "users.views.user_edit",
        name="manage_user_edit"),

    # product ---------------------------------------------------------------
    # manage
    url(r"^products/$",
        "products.views.products_list",
        name="manage_products"),

    # ajax details
    url(r"^products/_detail/(?P<product_id>\d+)/$",
        "products.views.product_details",
        name="manage_product_details"),

    # add
    url(r"^product/add/$",
        "products.views.product_add",
        name="manage_product_add"),

    # edit
    url(r"^product/(?P<product_id>\d+)/$",
        "products.views.product_edit",
        name="manage_product_edit"),

    # productversion ---------------------------------------------------------
    # manage
    url(r"^productversions/$",
        "productversions.views.productversions_list",
        name="manage_productversions"),

    # ajax details
    url(r"^productversions/_detail/(?P<productversion_id>\d+)/$",
        "productversions.views.productversion_details",
        name="manage_productversion_details"),

    # add
    url(r"^productversion/add/$",
        "productversions.views.productversion_add",
        name="manage_productversion_add"),

    # edit
    url(r"^productversion/(?P<productversion_id>\d+)/$",
        "productversions.views.productversion_edit",
        name="manage_productversion_edit"),

    # run --------------------------------------------------------------------
    # manage
    url(r"^runs/$",
        "runs.views.runs_list",
        name="manage_runs"),

    # ajax details
    url(r"^runs/_detail/(?P<run_id>\d+)/$",
        "runs.views.run_details",
        name="manage_run_details"),

    # add
    url(r"^run/add/$",
        "runs.views.run_add",
        name="manage_run_add"),

    # edit
    url(r"^run/(?P<run_id>\d+)/$",
        "runs.views.run_edit",
        name="manage_run_edit"),

    # suite ------------------------------------------------------------------
    # manage
    url(r"^suites/$",
        "suites.views.suites_list",
        name="manage_suites"),

    # ajax details
    url(r"^suites/_detail/(?P<suite_id>\d+)/$",
        "suites.views.suite_details",
        name="manage_suite_details"),

    # add
    url(r"^suite/add/$",
        "suites.views.suite_add",
        name="manage_suite_add"),

    # edit
    url(r"^suite/(?P<suite_id>\d+)/$",
        "suites.views.suite_edit",
        name="manage_suite_edit"),

    # testcase ---------------------------------------------------------------
    # manage
    url(r"^cases/$",
        "cases.views.cases_list",
        name="manage_cases"),

    # ajax details
    url(r"^cases/_detail/(?P<caseversion_id>\d+)/$",
        "cases.views.case_details",
        name="manage_case_details"),

    # add
    url(r"^case/add/$",
        "cases.views.case_add",
        name="manage_case_add"),

    # add bulk
    url(r"^case/add/bulk/$",
        "cases.views.case_add_bulk",
        name="manage_case_add_bulk"),

    # edit
    url(r"^case/version/(?P<caseversion_id>\d+)/$",
        "cases.views.caseversion_edit",
        name="manage_caseversion_edit"),

    # new version
    url(r"^case/version/(?P<caseversion_id>\d+)/clone/$",
        "cases.views.caseversion_clone",
        name="manage_caseversion_clone"),

    # tags -------------------------------------------------------------------
    # manage
    url(r"^tags/$",
        "tags.views.tags_list",
        name="manage_tags"),

    # ajax details
    url(r"^tags/_detail/(?P<tag_id>\d+)/$",
        "tags.views.tag_details",
        name="manage_tag_details"),

    # add
    url(r"^tag/add/$",
        "tags.views.tag_add",
        name="manage_tag_add"),

    # edit
    url(r"^tag/(?P<tag_id>\d+)/$",
        "tags.views.tag_edit",
        name="manage_tag_edit"),

    # autocomplete
    url(r"^tags/_autocomplete/",
        "tags.views.tag_autocomplete",
        name="manage_tags_autocomplete"),
)
