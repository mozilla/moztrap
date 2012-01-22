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
Tests for ajax view utilities.

"""
from mock import Mock

from django.template.response import TemplateResponse
from django.test import RequestFactory
from django.utils.unittest import TestCase



class AjaxTest(TestCase):
    @property
    def ajax(self):
        """The decorator under test."""
        from cc.core.ajax import ajax
        return ajax


    @property
    def view(self):
        """A simple TemplateResponse-returning view, decorated with @ajax."""
        @self.ajax("ajax_template.html")
        def view(request):
            return TemplateResponse(request, "normal_template.html")

        return view


    """Tests for ajax template-swapping view decorator."""
    def test_swaps_template(self):
        """Decorator changes TemplateResponse to given template, if ajax."""
        request = RequestFactory().get(
            "/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        response = self.view(request)
        self.assertEqual(response.template_name, "ajax_template.html")


    def test_only_ajax(self):
        """Decorator has no effect on non-Ajax response."""
        request = RequestFactory().get("/")
        response = self.view(request)
        self.assertEqual(response.template_name, "normal_template.html")
