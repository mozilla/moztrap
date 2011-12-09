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
from django.core.exceptions import MiddlewareNotUsed
from django.utils.unittest import TestCase

# not in Django 1.3, will be in 1.4
from djangosecure.test_utils import override_settings
from mock import patch, Mock


class AjaxTracebackMiddlewareTest(TestCase):
    @property
    def middleware(self):
        from cc.debug.middleware import AjaxTracebackMiddleware
        return AjaxTracebackMiddleware


    @override_settings(DEBUG=True)
    def test_used_in_DEBUG(self):
        self.middleware()


    @override_settings(DEBUG=False)
    def test_not_used_when_DEBUG_off(self):
        with self.assertRaises(MiddlewareNotUsed):
            self.middleware()


    @override_settings(DEBUG=True)
    def test_process_exception(self):
        """
        process_exception ajax response: traceback with <br>s inserted.

        """
        m = self.middleware()

        request = Mock()
        request.is_ajax.return_value = True

        with patch("traceback.format_exc") as format_exc:
            format_exc.return_value = "some\ntraceback"
            response = m.process_exception(request)

        self.assertEqual(response.content, "some<br>\ntraceback")


    @override_settings(DEBUG=True)
    def test_process_exception_non_ajax(self):
        """
        process_exception does nothing for non-ajax requests.

        """
        m = self.middleware()

        request = Mock()
        request.is_ajax.return_value = False

        self.assertIs(m.process_exception(request), None)
