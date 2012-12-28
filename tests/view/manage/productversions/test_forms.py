"""
Tests for productversion-management forms.

"""
from tests import case



class EditProductVersionFormTest(case.DBTestCase):
    """Tests for EditProductVersionForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.productversions.forms import EditProductVersionForm
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


    def test_edit_fill_from_2_missing(self):
        """Fill from a pv that has 2 cases missing from this one."""
        pv1 = self.F.ProductVersionFactory(version="1.0", codename="Foo")
        pv_fill_from = self.F.ProductVersionFactory(product=pv1.product, version="2.0")
        pv1 = self.refresh(pv1)

        # cv existing in both
        cv_exist = self.F.CaseVersionFactory(productversion=pv1)
        self.F.CaseVersionFactory(
            case=cv_exist.case,
            productversion=pv_fill_from,
            )

        # cvs we will end up with
        cv_new1 = self.F.CaseVersionFactory(
            productversion=pv_fill_from,
            name="noclone")
        exp_cvs = [
            cv_new1.case.id,
            self.F.CaseVersionFactory(productversion=pv_fill_from).case.id,
            cv_exist.case.id,
            ]

        f = self.form(
            {
                "version": "1.0",
                "fill_from": str(pv_fill_from.id),
                "cc_version": str(pv1.cc_version)
            },
            instance=pv1,
            )

        productversion = f.save()

        self.assertEqual(
            set(productversion.caseversions.all().values_list(
                "case_id", flat=True)),
            set(exp_cvs),
            )
        self.assertEqual(
            cv_new1.name,
            productversion.caseversions.get(case=cv_new1.case).name,
            )


    def test_edit_fill_from_2_missing_1_extra(self):
        """Fill from a pv get 2, this has 1 extra."""
        pv1 = self.F.ProductVersionFactory(version="1.0", codename="Foo")
        pv_fill_from = self.F.ProductVersionFactory(product=pv1.product, version="2.0")
        pv1 = self.refresh(pv1)

        cv1 = self.F.CaseVersionFactory(productversion=pv1)

        # cv existing in both
        cv_shared = self.F.CaseVersionFactory(productversion=pv1)
        self.F.CaseVersionFactory(
            case=cv_shared.case,
            productversion=pv_fill_from,
            )

        # cvs we will end up with
        exp_cvs = [
            self.F.CaseVersionFactory(productversion=pv_fill_from).case.id,
            self.F.CaseVersionFactory(productversion=pv_fill_from).case.id,
            cv_shared.case.id,
            cv1.case.id
            ]

        f = self.form(
            {
                "version": "1.0",
                "fill_from": str(pv_fill_from.id),
                "cc_version": str(pv1.cc_version)
            },
            instance=pv1,
            )

        productversion = f.save()

        self.assertEqual(
            set(productversion.caseversions.all().values_list(
                "case_id", flat=True)),
            set(exp_cvs),
            )


    def test_edit_fill_from_0_missing(self):
        """Fill from a pv that has 2 cases missing from this one."""
        pv1 = self.F.ProductVersionFactory(version="1.0", codename="Foo")
        pv_fill_from = self.F.ProductVersionFactory(product=pv1.product, version="2.0")
        pv1 = self.refresh(pv1)

        cv1 = self.F.CaseVersionFactory(productversion=pv1)

        # cv existing in both
        cv_shared = self.F.CaseVersionFactory(productversion=pv1)
        self.F.CaseVersionFactory(
            case=cv_shared.case,
            productversion=pv_fill_from,
            )

        # cvs we will end up with
        exp_cvs = [
            cv_shared.case.id,
            cv1.case.id
        ]

        f = self.form(
            {
                "version": "1.0",
                "fill_from": str(pv_fill_from.id),
                "cc_version": str(pv1.cc_version)
            },
            instance=pv1,
            )

        productversion = f.save()

        self.assertEqual(
            set(productversion.caseversions.all().values_list(
                "case_id", flat=True)),
            set(exp_cvs),
            )




class AddProductVersionFormTest(case.DBTestCase):
    """Tests for AddProductVersionForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.productversions.forms import AddProductVersionForm
        return AddProductVersionForm


    def test_add_productversion(self):
        """Can add productversion; sets created-by user, clones envs/cases."""
        pv = self.F.ProductVersionFactory.create(version="1.0")
        envs = self.F.EnvironmentFactory.create_full_set({"OS": ["Linux"]})
        pv.environments.add(*envs)
        cv = self.F.CaseVersionFactory.create(productversion=pv)
        u = self.F.UserFactory()

        f = self.form(
            {
                "product": str(pv.product.id),
                "version": "2.0",
                "clone_from": str(pv.id),
                "codename": "Foo",
                "cc_version": "0",
                },
            user=u
            )

        self.assertTrue(f.is_valid(), f.errors)

        productversion = f.save()

        self.assertEqual(productversion.product, pv.product)
        self.assertEqual(set(productversion.environments.all()), set(envs))
        new_cv = productversion.caseversions.get()
        self.assertEqual(new_cv.case, cv.case)
        self.assertEqual(new_cv.name, cv.name)
        self.assertEqual(productversion.version, "2.0")
        self.assertEqual(productversion.codename, "Foo")
        self.assertEqual(productversion.created_by, u)
