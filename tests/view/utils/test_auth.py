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
Tests for auth view utilities.

"""
from django.http import HttpResponse
from django.test import RequestFactory

from django.contrib.auth.models import AnonymousUser

# @@@ import from Django in 1.4
from djangosecure.test_utils import override_settings

from tests import case



class AjaxTest(case.TestCase):
    @property
    def login_maybe_required(self):
        """The decorator-factory under test."""
        from cc.view.utils.auth import login_maybe_required
        return login_maybe_required


    @property
    def view(self):
        """A simple view, decorated with @login_maybe_required."""
        @self.login_maybe_required
        def view(request):
            return HttpResponse("success")

        return view


    @override_settings(ALLOW_ANONYMOUS_ACCESS=False)
    def test_no_anonymous(self):
        """With no anonymous access, decorator requires login."""
        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        response = self.view(request)
        self.assertEqual(response.status_code, 302)


    @override_settings(ALLOW_ANONYMOUS_ACCESS=True)
    def test_anonymous(self):
        """With anonymous access allowed, decorator is no-op."""
        request = RequestFactory().get("/")
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "success")
