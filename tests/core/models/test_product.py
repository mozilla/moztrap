from django.test import TestCase


class ProductTest(TestCase):
    @property
    def model(self):
        from cc.core.models import Product
        return Product


    def test_unicode(self):
        p = self.model(name="Foo")

        self.assertEqual(unicode(p), u"Foo")
