"""
Tests for Environment model.

"""
from tests import case



class EnvironmentTest(case.DBTestCase):
    def test_unicode(self):
        """Unicode representation is concatenated element names."""
        e = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X"], "Language": ["English"]})[0]

        self.assertEqual(unicode(e), u"English, OS X")


    def test_ordered_elements(self):
        """ordered_elements yields elements in category name order."""
        e = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X"], "Language": ["English"]})[0]

        self.assertEqual(
            [el.name for el in e.ordered_elements()], [u"English", u"OS X"])


    def test_clone(self):
        """Cloning an environment clones element relationships."""
        e = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X"], "Language": ["English"]})[0]

        new = e.clone()

        self.assertEqual(set(new.elements.all()), set(e.elements.all()))


    def test_delete_prevention(self):
        """Deleting env used in a productversion raises ProtectedError."""
        env = self.F.EnvironmentFactory.create()
        self.F.ProductVersionFactory.create(environments=[env])

        with self.assertRaises(self.model.ProtectedError):
            env.delete()


    def test_delete_prevention_ignores_deleted_product_versions(self):
        """Can delete env used only by a deleted product version."""
        env = self.F.EnvironmentFactory.create()
        pv = self.F.ProductVersionFactory.create(environments=[env])

        pv.delete()

        env.delete()

        self.assertFalse(self.refresh(env).deleted_on is None)


    def test_deletable(self):
        """deletable property is False if env is used by a ProductVersion."""
        env = self.F.EnvironmentFactory.create()
        self.F.ProductVersionFactory.create(environments=[env])

        self.assertFalse(env.deletable)


    def test_deletable_ignores_deleted_envs(self):
        """deletable property is True if env used by deleted ProductVersion."""
        env = self.F.EnvironmentFactory.create()
        pv = self.F.ProductVersionFactory.create(environments=[env])

        pv.delete()

        self.assertTrue(env.deletable)


    def test_remove_from_profile_not_in_use(self):
        """If an environment is not in use, remove_from_profile deletes it."""
        el = self.F.ElementFactory.create()
        p = self.model.Profile.generate("Foo", el)
        env = p.environments.get()
        u = self.F.UserFactory()

        env.remove_from_profile(user=u)

        self.assertEqual(self.refresh(env).deleted_by, u)


    def test_remove_from_profile_in_use(self):
        """If an env is in use, remove_from_profile unsets its profile FK."""
        el = self.F.ElementFactory.create()
        p = self.model.Profile.generate("Foo", el)
        env = p.environments.get()
        u = self.F.UserFactory()
        self.F.ProductVersionFactory.create(environments=[env])

        env.remove_from_profile(user=u)

        env = self.refresh(env)
        self.assertEqual(env.profile, None)
        self.assertEqual(env.modified_by, u)
