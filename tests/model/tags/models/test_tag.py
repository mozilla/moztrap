"""
Tests for Tag model.

"""
from tests import case



class TagTest(case.DBTestCase):
    def test_unicode(self):
        """Unicode representation is name of Tag"""
        t = self.F.TagFactory(name="security")

        self.assertEqual(unicode(t), u"security")


    def test_clone(self):
        """Cloning sets 'cloned: ' prefix on name."""
        t = self.F.TagFactory(name="foo")

        new = t.clone()

        self.assertEqual(new.name, "Cloned: foo")
