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
Account-related URLs.

"""
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template



urlpatterns = patterns(
    "cc.view.users.views",

    # auth -------------------------------------------------------------------

    url(r"^login/", "login", name="auth_login"),
    url(r"^logout/", "logout", name="auth_logout"),
    url(r"^password/change/$", "password_change", name="auth_password_change"),
    url(r"^password/reset/$", "password_reset", name="auth_password_reset"),
    url(r"^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        "password_reset_confirm",
        name="auth_password_reset_confirm"),

    # registration -----------------------------------------------------------

    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r"^activate/(?P<activation_key>\w+)/$",
        "activate",
        name="registration_activate"),
    url(r"^register/$",
        "register",
        name="registration_register"),
    url(r"^register/closed/$",
        direct_to_template,
        {"template": "users/registration_closed.html"},
        name="registration_disallowed"),
    )
