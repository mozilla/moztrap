"""
Tests for suite-management forms.

"""
from tests import case



class EditSuiteFormTest(case.DBTestCase):
    """Tests for EditSuiteForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.suites.forms import EditSuiteForm
        return EditSuiteForm


    def test_edit_suite(self):
        """Can edit suite, including new product, sets modified-by."""
        p = self.F.ProductFactory()
        s = self.F.SuiteFactory()
        u = self.F.UserFactory()

        f = self.form(
            {
                "product": str(p.id),
                "name": "new name",
                "description": "new desc",
                "status": "draft",
                "cc_version": str(s.cc_version),
                },
            instance=s,
            user=u)

        suite = f.save()

        self.assertEqual(suite.product, p)
        self.assertEqual(suite.name, "new name")
        self.assertEqual(suite.description, "new desc")
        self.assertEqual(suite.modified_by, u)


    def test_no_change_product_option(self):
        """No option to change to different product if there are cases."""
        self.F.ProductFactory.create()
        s = self.F.SuiteFactory()
        self.F.SuiteCaseFactory(suite=s)

        f = self.form(instance=s)
        self.assertEqual(
            [c[0] for c in f.fields["product"].choices],
            ['', s.product.id]
            )
        self.assertTrue(f.fields["product"].readonly)


    def test_no_edit_product(self):
        """Can't change product if there are cases"""
        p = self.F.ProductFactory()
        s = self.F.SuiteFactory()
        self.F.SuiteCaseFactory(suite=s)

        f = self.form(
            {
                "product": str(p.id),
                "name": "new name",
                "description": "new desc",
                "status": "draft",
                "cc_version": str(s.cc_version),
                },
            instance=s,
            )

        self.assertFalse(f.is_valid())
        self.assertEqual(
            f.errors["product"],
            [u"Select a valid choice. "
             "That choice is not one of the available choices."]
            )


    def test_add_cases(self):
        """Can add cases to a suite."""
        s = self.F.SuiteFactory()
        c = self.F.CaseFactory(product=s.product)

        f = self.form(
            {
                "product": str(s.product.id),
                "name": s.name,
                "description": s.description,
                "status": s.status,
                "cases": [str(c.id)],
                "cc_version": str(s.cc_version),
                },
            instance=s,
            )

        self.assertTrue(f.is_valid())
        suite = f.save()

        self.assertEqual(set(suite.cases.all()), set([c]))


    def test_add_bad_case(self):
        """Try to add a non-existent case to a suite, get exception."""
        s = self.F.SuiteFactory()
        c = self.F.CaseFactory(product=s.product)

        f = self.form(
            {
                "product": str(s.product.id),
                "name": s.name,
                "description": s.description,
                "status": s.status,
                "cases": [str(c.id + 1)],
                "cc_version": str(s.cc_version),
                },
            instance=s,
            )

        self.assertFalse(f.is_valid())
        self.assertEqual(
            f.errors["cases"],
            [u"Not a valid case for this suite."]
        )


    def test_edit_cases(self):
        """Can edit cases of a suite."""
        s = self.F.SuiteFactory.create()
        self.F.SuiteCaseFactory.create(suite=s)
        c = self.F.CaseFactory.create(product=s.product)

        f = self.form(
            {
                "product": str(s.product.id),
                "name": s.name,
                "description": s.description,
                "status": s.status,
                "cases": [str(c.id)],
                "cc_version": str(s.cc_version),
                },
            instance=s,
            )

        self.assertTrue(f.is_valid())
        suite = f.save()

        self.assertEqual(set(suite.cases.all()), set([c]))


    def test_edit_cases_order_only(self):
        """Can edit cases of a suite."""
        s = self.F.SuiteFactory.create()
        c1 = self.F.CaseFactory.create(product=s.product)
        c2 = self.F.CaseFactory.create(product=s.product)
        self.F.SuiteCaseFactory.create(suite=s, case=c1, order=0)
        self.F.SuiteCaseFactory.create(suite=s, case=c2, order=1)

        f = self.form(
            {
                "product": str(s.product.id),
                "name": s.name,
                "description": s.description,
                "status": s.status,
                "cases": [str(c2.id), str(c1.id)],
                "cc_version": str(s.cc_version),
                },
            instance=s,
            )

        self.assertTrue(f.is_valid())
        suite = f.save()

        self.assertEqual(
            list(suite.cases.all().order_by("suitecases__order")),
            [c2, c1],
            )


    def test_remove_dup_cases(self):
        """Can edit cases of a suite."""
        s = self.F.SuiteFactory.create()
        c = self.F.CaseFactory.create(product=s.product)
        self.F.SuiteCaseFactory.create(suite=s, case=c)
        self.F.SuiteCaseFactory.create(suite=s, case=c)

        f = self.form(
            {
                "product": str(s.product.id),
                "name": s.name,
                "description": s.description,
                "status": s.status,
                "cases": [str(c.id), str(c.id)],
                "cc_version": str(s.cc_version),
                },
            instance=s,
            )

        self.assertTrue(f.is_valid())
        suite = f.save()

        self.assertEqual(set(suite.cases.all()), set([c]))



class AddSuiteFormTest(case.DBTestCase):
    """Tests for AddSuiteForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.suites.forms import AddSuiteForm
        return AddSuiteForm


    def test_add_suite(self):
        """Can add suite, has created-by user."""
        p = self.F.ProductFactory()
        u = self.F.UserFactory()

        f = self.form(
            {
                "product": str(p.id),
                "name": "Foo",
                "description": "foo desc",
                "status": "active",
                "cc_version": "0",
                },
            user=u
            )

        suite = f.save()

        self.assertEqual(suite.product, p)
        self.assertEqual(suite.name, "Foo")
        self.assertEqual(suite.description, "foo desc")
        self.assertEqual(suite.created_by, u)


    def test_initial_state(self):
        """New suites should default to active state."""
        form = self.form()

        self.assertEqual(form["status"].value(), "active")


    def test_add_with_cases(self):
        """Can add cases to a new suite."""
        c = self.F.CaseFactory()

        f = self.form(
            {
                "product": str(c.product.id),
                "name": "some name",
                "description": "some desc",
                "status": "active",
                "cases": [str(c.id)],
                "cc_version": "0",
                },
            )

        self.assertTrue(f.is_valid())
        suite = f.save()

        self.assertEqual(set(suite.cases.all()), set([c]))


    def test_product_id_attrs(self):
        """Product and cases options have data-product-id."""
        case = self.F.CaseFactory.create()

        f = self.form()

        self.assertEqual(
            [
                c[1].attrs["data-product-id"]
                for c in f.fields["product"].choices
                if c[0]
                ],
            [case.product.id]
            )
