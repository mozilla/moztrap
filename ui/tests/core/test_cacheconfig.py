"""
Tests for global Django caching config.

"""
from unittest2 import TestCase



class MakeKeyTest(TestCase):
    @property
    def func(self):
        from tcmui.core.cacheconfig import make_key
        return make_key


    def test_make_key(self):
        self.assertEqual(
            self.func("key", "prefix", 4),
            "131ad3a66fb91dd513d364c8a7a35eacb9084757")
