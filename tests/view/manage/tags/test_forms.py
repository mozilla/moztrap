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
                "description": "new desc",
                "cc_version": str(t.cc_version),
                },
            instance=t,
            user=u,
            )

        tag = f.save()

        self.assertEqual(tag.name, "Two")
        self.assertEqual(tag.product, p2)
        self.assertEqual(tag.description, "new desc")
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


    def test_add_cases(self):
        """Can add cases to a tag."""
        cv = self.F.CaseVersionFactory()
        t = self.F.TagFactory(product=cv.productversion.product)

        f = self.form(
            {
                "product": str(t.product.id),
                "name": t.name,
                "description": t.description,
                "caseversions": [str(cv.id)],
                "cc_version": str(t.cc_version),
                },
            instance=t,
            )

        self.assertTrue(f.is_valid())
        tag = f.save()

        self.assertEqual(set(tag.caseversions.all()), set([cv]))


    def test_add_bad_case(self):
        """Try to add a non-existent case to a tag, get exception."""
        cv = self.F.CaseVersionFactory()
        t = self.F.TagFactory(product=cv.productversion.product)

        f = self.form(
            {
                "product": str(t.product.id),
                "name": t.name,
                "description": t.description,
                "caseversions": [str(cv.id+1)],
                "cc_version": str(t.cc_version),
                },
            instance=t,
            )

        self.assertFalse(f.is_valid())
        self.assertEqual(
            f.errors["caseversions"],
            [u"Not a valid caseversion for this tag."]
        )


    def test_edit_cases(self):
        """Can edit cases of a tag."""
        pv = self.F.ProductVersionFactory()
        t = self.F.TagFactory(product=pv.product)
        t.caseversions.add(self.F.CaseVersionFactory(productversion=pv))
        cv_new = self.F.CaseVersionFactory(productversion=pv)

        f = self.form(
            {
                "product": str(t.product.id),
                "name": t.name,
                "description": t.description,
                "caseversions": [str(cv_new.id)],
                "cc_version": str(t.cc_version),
                },
            instance=t,
            )

        self.assertTrue(f.is_valid())
        tag = f.save()

        self.assertEqual(set(tag.caseversions.all()), set([cv_new]))



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
            {
                "name": "Two",
                "product": str(p.id),
                "description": "foo desc",
                "cc_version": "0",
                },
            user=u)

        tag = f.save()

        self.assertEqual(tag.name, "Two")
        self.assertEqual(tag.product, p)
        self.assertEqual(tag.description, "foo desc")
        self.assertEqual(tag.created_by, u)


    def test_add_with_cases(self):
        """Can add cases to a new tag."""
        cv = self.F.CaseVersionFactory()

        f = self.form(
            {
                "product": str(cv.productversion.product.id),
                "name": "some name",
                "description": "some desc",
                "caseversions": [str(cv.id)],
                "cc_version": 0,
                },
            )

        self.assertTrue(f.is_valid())
        tag = f.save()

        self.assertEqual(set(tag.caseversions.all()), set([cv]))


    def test_product_id_attrs(self):
        """Product and cases options have data-product-id."""
        cv = self.F.CaseVersionFactory.create()

        f = self.form()

        self.assertEqual(
            [
            c[1].attrs["data-product-id"]
            for c in f.fields["product"].choices
            if c[0]
            ],
            [cv.productversion.product.id]
        )
