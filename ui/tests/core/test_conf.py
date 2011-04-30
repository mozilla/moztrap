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
        from tcmui.core.conf import Configuration
        return Configuration


    def test_default(self):
        conf = self.cls(SOME_SETTING="some val")

        settings = FakeSettings()
        with patch("tcmui.core.conf.settings", settings):
            val = conf.SOME_SETTING

        self.assertEqual(val, "some val")
        self.assertEqual(settings.failed, ["SOME_SETTING"])


    def test_no_default(self):
        from django.core.exceptions import ImproperlyConfigured

        conf = self.cls()

        settings = FakeSettings()
        with patch("tcmui.core.conf.settings", settings):
            with self.assertRaises(ImproperlyConfigured):
                conf.SOME_SETTING

        self.assertEqual(settings.failed, ["SOME_SETTING"])


    def test_exists(self):
        conf = self.cls()

        settings = FakeSettings(SOME_SETTING="a val")
        with patch("tcmui.core.conf.settings", settings):
            val = conf.SOME_SETTING

        self.assertEqual(val, "a val")
        self.assertEqual(settings.accessed, ["SOME_SETTING"])


    def test_default_is_fallback(self):
        conf = self.cls(SOME_SETTING="default val")

        settings = FakeSettings(SOME_SETTING="set val")
        with patch("tcmui.core.conf.settings", settings):
            val = conf.SOME_SETTING

        self.assertEqual(val, "set val")
        self.assertEqual(settings.accessed, ["SOME_SETTING"])
