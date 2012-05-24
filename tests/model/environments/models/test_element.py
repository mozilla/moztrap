"""
Tests for Element model.

"""
from tests import case



class ElementTest(case.DBTestCase):
    """Tests for Element model."""
    def test_unicode(self):
        """Unicode representation is name of element."""
        e = self.F.ElementFactory.build(name="Windows 7")

        self.assertEqual(unicode(e), u"Windows 7")


    def test_delete_prevention(self):
        """Deleting element included in an environment raises ProtectedError."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        with self.assertRaises(self.model.ProtectedError):
            el.delete()


    def test_delete_prevention_ignores_deleted_envs(self):
        """Can delete element included only in a deleted environment."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        env.delete()

        el.delete()

        self.assertFalse(self.refresh(el).deleted_on is None)


    def test_deletable(self):
        """deletable property is False if element is included in an env."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        self.assertFalse(el.deletable)


    def test_deletable_ignores_deleted_envs(self):
        """deletable property is True if element is in a deleted environment."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        env.delete()

        self.assertTrue(el.deletable)
