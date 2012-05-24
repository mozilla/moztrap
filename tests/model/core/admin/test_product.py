"""
Tests for Product admin.

"""
from tests import case



class ProductAdminTest(case.admin.AdminTestCase):
    app_label = "core"
    model_name = "product"


    def test_changelist(self):
        """Product changelist page loads without error, contains name."""
        self.F.ProductFactory.create(name="Firefox")

        self.get(self.changelist_url).mustcontain("Firefox")


    def test_change_page(self):
        """Product change page loads without error, contains name."""
        p = self.F.ProductFactory.create(name="Firefox")

        self.get(self.change_url(p)).mustcontain("Firefox")


    def test_change_tracks_user(self):
        """Making a change via the admin tracks modified-by user."""
        p = self.F.ProductFactory.create(name="Firefox")
        url = self.change_url(p)
        form = self.get(url).forms[0]
        form["name"] = "Fennec"

        res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(self.refresh(p).modified_by, self.user)


    def test_delete_tracks_user(self):
        """Deletion via the admin tracks deleted-by user."""
        p = self.F.ProductFactory.create(name="Firefox")
        url = self.delete_url(p)
        form = self.get(url).forms[0]

        res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(self.refresh(p).deleted_by, self.user)


    def test_bulk_delete_tracks_user(self):
        """Deletion via bulk-action tracks deleted-by user."""
        p = self.F.ProductFactory.create(name="Firefox")
        form = self.get(self.changelist_url).forms["changelist-form"]
        form["action"] = "delete"
        form["_selected_action"] = str(p.id)
        form.submit("index", 0)

        self.assertEqual(self.refresh(p).deleted_by, self.user)


    def test_bulk_undelete(self):
        """Bulk undelete action works."""
        p = self.F.ProductFactory.create(name="Firefox")
        p.delete()
        form = self.get(self.changelist_url).forms["changelist-form"]
        form["action"] = "undelete"
        form["_selected_action"] = str(p.id)
        form.submit("index", 0)

        self.assertEqual(self.refresh(p).deleted_on, None)


    def test_hard_delete(self):
        """Hard deletion via bulk-action really deletes."""
        p = self.F.ProductFactory.create(name="Firefox")
        form = self.get(self.changelist_url).forms["changelist-form"]
        form["action"] = "delete_selected"
        form["_selected_action"] = str(p.id)
        form.submit("index", 0).forms[0].submit()

        self.assertEqual(p.__class__.objects.count(), 0)
