"""
Tests for tag management forms.

"""
from tests import case



class EditTagFormTest(case.DBTestCase):
    """Tests for EditTagForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.tags.forms import EditTagForm
        return EditTagForm


    def test_edit_tag(self):
        """Can edit tag name and product, with modified-by user."""
        p = self.F.ProductFactory.create()
        p2 = self.F.ProductFactory.create()
        t = self.F.TagFactory.create(name="Take One", product=p)
        u = self.F.UserFactory.create()

        f = self.form(
            {
                "name": "Two",
                "product": str(p2.id),
                "cc_version": str(t.cc_version),
                },
            instance=t,
            user=u,
            )

        tag = f.save()

        self.assertEqual(tag.name, "Two")
        self.assertEqual(tag.product, p2)
        self.assertEqual(tag.modified_by, u)


    def test_no_edit_product_if_tagged(self):
        """Can't change tag product if tag is in use."""
        p = self.F.ProductFactory.create()
        p2 = self.F.ProductFactory.create()
        cv = self.F.CaseVersionFactory.create(case__product=p, productversion__product=p)
        t = self.F.TagFactory.create(name="Take One", product=p)
        cv.tags.add(t)

        f = self.form(
            {"name": "Two", "product": str(p2.id)}, instance=t)

        self.assertFalse(f.is_valid())
        self.assertEqual(
            f.errors["product"],
            [u"Select a valid choice. "
             "That choice is not one of the available choices."]
            )


    def test_no_set_product_if_multiple_products_tagged(self):
        """Can't set tag product if cases from multiple products are tagged."""
        p = self.F.ProductFactory.create()
        p2 = self.F.ProductFactory.create()
        cv = self.F.CaseVersionFactory.create(
            case__product=p, productversion__product=p)
        cv2 = self.F.CaseVersionFactory.create(
            case__product=p2, productversion__product=p2)
        t = self.F.TagFactory.create(name="Take One")
        cv.tags.add(t)
        cv2.tags.add(t)

        f = self.form(
            {"name": "Two", "product": str(p.id)}, instance=t)

        self.assertFalse(f.is_valid())
        self.assertEqual(
            f.errors["product"],
            [u"Select a valid choice. "
             "That choice is not one of the available choices."]
            )



class AddTagFormTest(case.DBTestCase):
    """Tests for AddTagForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.tags.forms import AddTagForm
        return AddTagForm


    def test_add_tag(self):
        """Can add tag, with product and created-by user."""
        p = self.F.ProductFactory.create()
        u = self.F.UserFactory()

        f = self.form(
            {"name": "Two", "product": str(p.id), "cc_version": "0"},
            user=u)

        tag = f.save()

        self.assertEqual(tag.name, "Two")
        self.assertEqual(tag.product, p)
        self.assertEqual(tag.created_by, u)
