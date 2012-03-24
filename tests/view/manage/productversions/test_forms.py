"""
Tests for productversion-management forms.

"""
from tests import case



class EditProductVersionFormTest(case.DBTestCase):
    """Tests for EditProductVersionForm."""
    @property
    def form(self):
        """The form class under test."""
        from cc.view.manage.productversions.forms import EditProductVersionForm
        return EditProductVersionForm


    def test_edit_productversion(self):
        """Can edit productversion version and codename, with modified-by."""
        p = self.F.ProductVersionFactory(version="1.0", codename="Foo")
        u = self.F.UserFactory()

        f = self.form(
            {
                "version": "2.0",
                "codename": "New",
                "cc_version": str(p.cc_version)
                },
            instance=p,
            user=u,
            )

        productversion = f.save()

        self.assertEqual(productversion.version, "2.0")
        self.assertEqual(productversion.codename, "New")
        self.assertEqual(productversion.modified_by, u)



class AddProductVersionFormTest(case.DBTestCase):
    """Tests for AddProductVersionForm."""
    @property
    def form(self):
        """The form class under test."""
        from cc.view.manage.productversions.forms import AddProductVersionForm
        return AddProductVersionForm


    def test_add_productversion(self):
        """Can add productversion; sets created-by user."""
        pv = self.F.ProductVersionFactory(version="1.0")
        envs = self.F.EnvironmentFactory.create_full_set({"OS": ["Linux"]})
        pv.environments.add(*envs)
        u = self.F.UserFactory()

        f = self.form(
            {
                "product": str(pv.product.id),
                "version": "2.0",
                "clone_envs_from": str(pv.id),
                "codename": "Foo",
                "cc_version": "0",
                },
            user=u
            )

        self.assertTrue(f.is_valid(), f.errors)

        productversion = f.save()

        self.assertEqual(productversion.product, pv.product)
        self.assertEqual(set(productversion.environments.all()), set(envs))
        self.assertEqual(productversion.version, "2.0")
        self.assertEqual(productversion.codename, "Foo")
        self.assertEqual(productversion.created_by, u)
