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
Tests for list actions.

"""
from mock import Mock

from django.http import HttpResponse
from django.test import RequestFactory
from django.utils.unittest import TestCase



class ActionsTest(TestCase):
    """Tests for list-actions decorator."""
    @property
    def actions(self):
        """The decorator under test."""
        from cc.manage.actions import actions
        return actions


    def setUp(self):
        """Set up a mock Model class."""
        self.mock_model = Mock()


    def view(self, request, decorator=None):
        """
        Pass request to decorated test view, return response.

        Optionally accepts decorator to apply. Assigns request as ``request``
        attribute on response.

        """
        if decorator is None:
            decorator = self.actions(self.mock_model, ["doit"])

        @decorator
        def view(req):
            response = HttpResponse()
            response.request = req
            return response

        return view(request)


    def test_action_redirects(self):
        """After action is taken, redirects to original URL."""
        req = RequestFactory().post("/the/url", data={"action-doit": "3"})

        res = self.view(req)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], "/the/url")


    def test_action_redirects_with_querystring(self):
        """Post-action redirect includes querystring."""
        req = RequestFactory().post(
            "/the/url?filter=value", data={"action-doit": "3"})

        res = self.view(req)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], "/the/url?filter=value")


    def test_ajax_no_redirect(self):
        """Ajax request doesn't redirect post-action."""
        req = RequestFactory().post(
            "/the/url?filter=value", data={"action-doit": "3"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        res = self.view(req)

        self.assertEqual(res.status_code, 200)


    def test_ajax_fall_through_method(self):
        """Post-action, ajax req continues with method GET and no POST data."""
        req = RequestFactory().post(
            "/the/url?filter=value", data={"action-doit": "3"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        res = self.view(req)

        self.assertEqual(res.request.method, "GET")
        self.assertEqual(res.request.POST, {})


    def test_action_called(self):
        """Correct method is called on correct object."""
        req = RequestFactory().post("/the/url", data={"action-doit": "3"})

        self.view(req)

        model_get = self.mock_model._base_manager.get
        model_get.assert_called_with(pk="3")

        instance = model_get.return_value
        instance.doit.assert_called_with()


    def test_POST_no_action(self):
        """Without fallthrough, redirects even if no action taken."""
        req = RequestFactory().post("/the/url", data={})

        res = self.view(req)

        self.assertEqual(self.mock_model._base_manager.get.call_count, 0)
        self.assertEqual(res.status_code, 302)


    def test_bad_action(self):
        """Unknown action is handled the same as no action."""
        req = RequestFactory().post("/the/url", data={"action-bad": "3"})

        res = self.view(req)

        self.assertEqual(self.mock_model._base_manager.get.call_count, 0)
        self.assertEqual(res.status_code, 302)


    def test_fall_through(self):
        """If fall_through is set, POST falls through untouched if no action."""
        dec = self.actions(self.mock_model, ["doit"], fall_through=True)
        req = RequestFactory().post("/the/url", data={"other": "thing"})

        res = self.view(req, decorator=dec)

        self.assertEqual(self.mock_model._base_manager.get.call_count, 0)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.request.method, "POST")
        self.assertEqual(res.request.POST["other"], "thing")
