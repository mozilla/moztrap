"""
Tests for Category model.

"""
from tests import case



class CategoryTest(case.DBTestCase):
    """Tests for Category model."""
    def test_unicode(self):
        """Unicode representation is name of category."""
        c = self.F.CategoryFactory(name="Operating System")

        self.assertEqual(unicode(c), u"Operating System")


    def test_delete_prevention(self):
        """Deleting category used in an environment raises ProtectedError."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        with self.assertRaises(self.model.ProtectedError):
            el.category.delete()


    def test_delete_prevention_ignores_deleted_envs(self):
        """Can delete category included only in a deleted environment."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        env.delete()

        el.category.delete()

        self.assertFalse(self.refresh(el.category).deleted_on is None)


    def test_deletable(self):
        """deletable property is False if category is included in an env."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        self.assertFalse(el.category.deletable)


    def test_deletable_ignores_deleted_envs(self):
        """deletable property is True if category is in deleted environment."""
        el = self.F.ElementFactory.create(name="Debian")
        env = self.F.EnvironmentFactory.create()
        env.elements.add(el)

        env.delete()

        self.assertTrue(el.category.deletable)
