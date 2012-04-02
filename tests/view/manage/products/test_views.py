"""
Tests for product management views.

"""
from django.core.urlresolvers import reverse

from tests import case



class ProductsTest(case.view.manage.ListViewTestCase,
                   case.view.ListFinderTests,
                   case.view.manage.CCModelListTests,
                   case.view.NoCacheTest,
                   ):
    """Test for products manage list view."""
    form_id = "manage-products-form"
    perm = "manage_products"


    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.ProductFactory


    @property
    def url(self):
        """Shortcut for manage-products url."""
        return reverse("manage_products")


    def test_filter_by_name(self):
        """Can filter by name."""
        self.factory.create(name="Product 1")
        self.factory.create(name="Product 2")

        res = self.get(params={"filter-name": "1"})

        self.assertInList(res, "Product 1")
        self.assertNotInList(res, "Product 2")


    def test_sort_by_name(self):
        """Can sort by name."""
        self.factory.create(name="Product 1")
        self.factory.create(name="Product 2")

        res = self.get(params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Product 2", "Product 1")



class ProductDetailTest(case.view.AuthenticatedViewTestCase,
                        case.view.NoCacheTest,
                        ):
    """Test for product-detail ajax view."""
    def setUp(self):
        """Setup for case details tests; create a product."""
        super(ProductDetailTest, self).setUp()
        self.product = self.F.ProductFactory.create()


    @property
    def url(self):
        """Shortcut for product detail url."""
        return reverse(
            "manage_product_details", kwargs=dict(product_id=self.product.id))


    def test_details_versions(self):
        """Details lists product versions."""
        self.F.ProductVersionFactory.create(
            product=self.product, version="0.8-alpha-1")

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("0.8-alpha-1")


    def test_details_team(self):
        """Details lists team."""
        u = self.F.UserFactory.create(username="somebody")
        self.product.add_to_team(u)

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("somebody")



class AddProductTest(case.view.FormViewTestCase,
                     case.view.NoCacheTest,
                     ):
    """Tests for add product view."""
    form_id = "product-add-form"


    @property
    def url(self):
        """Shortcut for add-product url."""
        return reverse("manage_product_add")


    def setUp(self):
        """Add manage-products permission to user."""
        super(AddProductTest, self).setUp()
        self.add_perm("manage_products")


    def test_success(self):
        """Can add a product with basic data, including a version."""
        form = self.get_form()
        form["name"] = "Some browser"
        form["description"] = "Some old browser or other."
        form["version"] = "1.0"

        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_products"))

        res.follow().mustcontain("Product 'Some browser' added.")

        p = self.model.Product.objects.get()
        self.assertEqual(p.name, "Some browser")
        self.assertEqual(p.description, "Some old browser or other.")
        self.assertEqual(p.versions.get().version, "1.0")


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_manage_products_permission(self):
        """Requires manage-products permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")



class EditProductTest(case.view.FormViewTestCase,
                      case.view.NoCacheTest,
                      ):
    """Tests for edit-product view."""
    form_id = "product-edit-form"


    def setUp(self):
        """Setup for product edit tests; create a product, add perm."""
        super(EditProductTest, self).setUp()
        self.product = self.F.ProductFactory.create()
        self.add_perm("manage_products")


    @property
    def url(self):
        """Shortcut for edit-product url."""
        return reverse(
            "manage_product_edit", kwargs=dict(product_id=self.product.id))


    def test_requires_manage_products_permission(self):
        """Requires manage-products permission."""
        res = self.app.get(self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")


    def test_save_basic(self):
        """Can save updates; redirects to manage products list."""
        form = self.get_form()
        form["name"] = "new name"
        form["description"] = "new desc"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_products"))

        res.follow().mustcontain("Saved 'new name'.")

        p = self.refresh(self.product)
        self.assertEqual(p.name, "new name")
        self.assertEqual(p.description, "new desc")


    def test_errors(self):
        """Test bound form redisplay with errors."""
        form = self.get_form()
        form["name"] = ""
        res = form.submit(status=200)

        res.mustcontain("This field is required.")


    def test_concurrency_error(self):
        """Concurrency error is displayed."""
        form = self.get_form()

        self.product.save()

        form["name"] = "New"
        res = form.submit(status=200)

        res.mustcontain("Another user saved changes to this object")
