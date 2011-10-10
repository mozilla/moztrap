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
from unittest2 import TestCase
from mock import patch


class FakeSettings(object):
    def __init__(self, **kwargs):
        self.accessed = []
        self.failed = []
        self.values = {}
        self.values.update(kwargs)


    def __getattr__(self, attr):
        try:
            val = self.values[attr]
        except KeyError:
            self.failed.append(attr)
            raise AttributeError
        else:
            self.accessed.append(attr)
            return val


class ConfigurationTest(TestCase):
    @property
    def cls(self):
        from ccui.core.conf import Configuration
        return Configuration


    def test_default(self):
        conf = self.cls(SOME_SETTING="some val")

        settings = FakeSettings()
        with patch("ccui.core.conf.settings", settings):
            val = conf.SOME_SETTING

        self.assertEqual(val, "some val")
        self.assertEqual(settings.failed, ["SOME_SETTING"])


    def test_no_default(self):
        from django.core.exceptions import ImproperlyConfigured

        conf = self.cls()

        settings = FakeSettings()
        with patch("ccui.core.conf.settings", settings):
            with self.assertRaises(ImproperlyConfigured):
                conf.SOME_SETTING

        self.assertEqual(settings.failed, ["SOME_SETTING"])


    def test_exists(self):
        conf = self.cls()

        settings = FakeSettings(SOME_SETTING="a val")
        with patch("ccui.core.conf.settings", settings):
            val = conf.SOME_SETTING

        self.assertEqual(val, "a val")
        self.assertEqual(settings.accessed, ["SOME_SETTING"])


    def test_default_is_fallback(self):
        conf = self.cls(SOME_SETTING="default val")

        settings = FakeSettings(SOME_SETTING="set val")
        with patch("ccui.core.conf.settings", settings):
            val = conf.SOME_SETTING

        self.assertEqual(val, "set val")
        self.assertEqual(settings.accessed, ["SOME_SETTING"])
