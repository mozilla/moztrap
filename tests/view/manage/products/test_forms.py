"""
Tests for product-management forms.

"""
from tests import case



class EditProductFormTest(case.DBTestCase):
    """Tests for EditProductForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.products.forms import EditProductForm
        return EditProductForm


    def test_edit_product(self):
        """Can edit product name and description, with modified-by user."""
        p = self.F.ProductFactory(name="Take One", description="")
        u = self.F.UserFactory()

        f = self.form(
            {
                "name": "Two",
                "description": "not blank",
                "cc_version": str(p.cc_version),
                },
            instance=p,
            user=u,
            )

        product = f.save()

        self.assertEqual(product.name, "Two")
        self.assertEqual(product.description, "not blank")
        self.assertEqual(product.modified_by, u)



class AddProductFormTest(case.DBTestCase):
    """Tests for AddProductForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.products.forms import AddProductForm
        return AddProductForm


    def test_add_product(self):
        """Can add product, with version and created-by user."""
        u = self.F.UserFactory()

        f = self.form(
            {
                "name": "Two",
                "version": "1.0",
                "description": "not blank",
                "cc_version": "0",
                },
            user=u)

        product = f.save()

        self.assertEqual(product.name, "Two")
        self.assertEqual(product.description, "not blank")
        self.assertEqual(product.created_by, u)

        version = product.versions.get()

        self.assertEqual(version.version, "1.0")
        self.assertEqual(version.created_by, u)


    def test_add_product_with_profile(self):
        """Can add product with initial environment profile."""
        profile = self.F.ProfileFactory.create()
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["OS X", "Linux"]}, profile=profile)

        f = self.form(
            {
                "name": "Two",
                "version": "1.0",
                "profile": profile.id,
                "cc_version": "0",
                }
            )

        version = f.save().versions.get()

        self.assertEqual(set(version.environments.all()), set(envs))
