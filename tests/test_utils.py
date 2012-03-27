from django.utils.unittest import TestCase



class TestUrl(TestCase):
    @property
    def url(self):
        from .utils import Url
        return Url


    def assertEqual(self, *args):
        """
        For this test, want to ensure that compare-equal implies hash-equal.

        """
        super(TestUrl, self).assertEqual(*args)

        super(TestUrl, self).assertEqual(hash(args[0]), hash(args[1]), args[2:])


    def test_no_qs(self):
        self.assertEqual(
            self.url("http://fake.base/path/"),
            self.url("http://fake.base/path/"))


    def test_same_qs(self):
        self.assertEqual(
            self.url("http://fake.base/path/?foo=bar"),
            self.url("http://fake.base/path/?foo=bar"))


    def test_different_key_order(self):
        self.assertEqual(
            self.url("http://fake.base/path/?foo=bar&arg=yo"),
            self.url("http://fake.base/path/?arg=yo&foo=bar"))


    def test_different_value_order(self):
        self.assertNotEqual(
            self.url("http://fake.base/path/?foo=bar&foo=yo"),
            self.url("http://fake.base/path/?foo=yo&foo=bar"))


    def test_repr(self):
        self.assertEqual(
            repr(self.url("http://fake.base/path/?foo=bar")),
            "Url(http://fake.base/path/?foo=bar)")
