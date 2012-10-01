"""
Tests for run-management forms.

"""
from datetime import date

from tests import case



class EditRunFormTest(case.DBTestCase):
    """Tests for EditRunForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.runs.forms import EditRunForm
        return EditRunForm


    def test_edit_run(self):
        """Can edit run, including productversion, with modified-by."""
        pv = self.F.ProductVersionFactory.create()
        r = self.F.RunFactory.create(productversion__product=pv.product)
        u = self.F.UserFactory.create()

        f = self.form(
            {
                "productversion": str(pv.id),
                "name": "new name",
                "description": "new desc",
                "start": "1/3/2012",
                "end": "1/10/2012",
                "cc_version": str(r.cc_version),
                },
            instance=r,
            user=u)

        run = f.save()

        self.assertEqual(run.productversion, pv)
        self.assertEqual(run.name, "new name")
        self.assertEqual(run.description, "new desc")
        self.assertEqual(run.start, date(2012, 1, 3))
        self.assertEqual(run.end, date(2012, 1, 10))
        self.assertEqual(run.modified_by, u)


    def test_add_suites(self):
        """Can add suites to a run."""
        pv = self.F.ProductVersionFactory.create()
        r = self.F.RunFactory.create(productversion__product=pv.product)
        s = self.F.SuiteFactory.create(product=pv.product)

        f = self.form(
            {
                "productversion": str(pv.id),
                "name": r.name,
                "description": r.description,
                "start": r.start.strftime("%m/%d/%Y"),
                "end": "",
                "suites": [str(s.id)],
                "cc_version": str(r.cc_version),
                },
            instance=r,
            )

        run = f.save()

        self.assertEqual(set(run.suites.all()), set([s]))


    def test_edit_suites(self):
        """Can edit suites in a run."""
        pv = self.F.ProductVersionFactory.create()
        r = self.F.RunFactory.create(productversion__product=pv.product)
        self.F.RunSuiteFactory.create(run=r)
        s = self.F.SuiteFactory.create(product=pv.product)

        f = self.form(
            {
                "productversion": str(pv.id),
                "name": r.name,
                "description": r.description,
                "start": r.start.strftime("%m/%d/%Y"),
                "end": "",
                "suites": [str(s.id)],
                "cc_version": str(r.cc_version),
                },
            instance=r,
            )

        run = f.save()

        self.assertEqual(set(run.suites.all()), set([s]))


    def test_no_change_product_option(self):
        """No option to change to a version of a different product."""
        self.F.ProductVersionFactory.create()
        r = self.F.RunFactory()

        f = self.form(instance=r)
        self.assertEqual(
            [c[0] for c in f.fields["productversion"].choices],
            ['', r.productversion.id]
            )


    def test_no_edit_product(self):
        """Can't change product"""
        pv = self.F.ProductVersionFactory()
        r = self.F.RunFactory()

        f = self.form(
            {
                "productversion": str(pv.id),
                "name": "new name",
                "description": "new desc",
                "start": "1/3/2012",
                "end": "1/10/2012",
                "cc_version": str(r.cc_version),
                },
            instance=r,
            )

        self.assertFalse(f.is_valid())
        self.assertEqual(
            f.errors["productversion"],
            [u"Select a valid choice. "
             "That choice is not one of the available choices."]
            )


    def test_active_run_no_product_version_options(self):
        """If editing active run, current product version is only option."""
        pv = self.F.ProductVersionFactory.create()
        r = self.F.RunFactory(
            status=self.model.Run.STATUS.active,
            productversion__product=pv.product)

        f = self.form(instance=r)
        self.assertEqual(
            [c[0] for c in f.fields["productversion"].choices],
            ['', r.productversion.id]
            )


    def test_active_run_product_version_readonly(self):
        """If editing active run, product version field is marked readonly."""
        pv = self.F.ProductVersionFactory.create()
        r = self.F.RunFactory(
            status=self.model.Run.STATUS.active,
            productversion__product=pv.product)

        f = self.form(instance=r)
        self.assertTrue(f.fields["productversion"].readonly)


    def test_active_run_no_edit_product_version(self):
        """Can't change product version of active run"""
        pv = self.F.ProductVersionFactory()
        r = self.F.RunFactory(status=self.model.Run.STATUS.active)

        f = self.form(
            {
                "productversion": str(pv.id),
                "name": "new name",
                "description": "new desc",
                "start": "1/3/2012",
                "end": "1/10/2012",
                "cc_version": str(r.cc_version),
                },
            instance=r,
            )

        self.assertFalse(f.is_valid())
        self.assertEqual(
            f.errors["productversion"],
            [u"Select a valid choice. "
             "That choice is not one of the available choices."]
            )


    def test_save_tags(self):
        """Can add/remove tags."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_tags"))

        r = self.F.RunFactory.create()

        t1 = self.F.TagFactory.create(name="one")
        t2 = self.F.TagFactory.create(name="two")
        t3 = self.F.TagFactory.create(name="three")

        r.tags.add(t1, t2)

        form = self.form(
            {
                "productversion": str(pv.id),
                "name": "new name",
                "description": "new desc",
                "tag-tag": [t2.id, t3.id],
                "tag-newtag": ["foo"],
                "start": "1/3/2012",
                "end": "1/10/2012",
                "cc_version": str(r.cc_version),
                },
            instance=r,
            )

        r = form.save()

        self.assertEqual(
            set([t.name for t in r.tags.all()]),
            set(["two", "three", "foo"])
        )



class AddRunFormTest(case.DBTestCase):
    """Tests for AddRunForm."""
    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.runs.forms import AddRunForm
        return AddRunForm


    def test_add_run(self):
        """Can add run, has created-by user."""
        pv = self.F.ProductVersionFactory()
        u = self.F.UserFactory()

        f = self.form(
            {
                "productversion": str(pv.id),
                "name": "Foo",
                "description": "foo desc",
                "start": "1/3/2012",
                "end": "1/10/2012",
                "cc_version": "0",
                },
            user=u
            )

        run = f.save()

        self.assertEqual(run.productversion, pv)
        self.assertEqual(run.name, "Foo")
        self.assertEqual(run.description, "foo desc")
        self.assertEqual(run.start, date(2012, 1, 3))
        self.assertEqual(run.end, date(2012, 1, 10))
        self.assertEqual(run.created_by, u)


    def test_add_run_withsuites(self):
        """Can add suites to a new run."""
        pv = self.F.ProductVersionFactory.create()
        s = self.F.SuiteFactory.create(product=pv.product)

        f = self.form(
            {
                "productversion": str(pv.id),
                "name": "some name",
                "description": "some desc",
                "start": "1/3/2012",
                "end": "",
                "suites": [str(s.id)],
                "cc_version": "0",
                },
            )

        run = f.save()

        self.assertEqual(set(run.suites.all()), set([s]))


    def test_tag_autocomplete_url(self):
        """Tag autocomplete field renders data-autocomplete-url."""
        self.assertIn(
            'data-autocomplete-url="{0}"'.format(
                reverse("manage_tags_autocomplete")),
            unicode(self.form()["add_tags"])
        )


    def test_tag(self):
        """Can tag a new case with some existing tags."""
        t1 = self.F.TagFactory.create(name="foo")
        t2 = self.F.TagFactory.create(name="bar")
        data = self.get_form_data()
        data.setlist("tag-tag", [t1.id, t2.id])

        r = self.form(data=data).save().versions.get()

        self.assertEqual(list(r.tags.all()), [t1, t2])


    def test_new_tag(self):
        """Can create a new case with a new tag, with correct perm."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_tags"))
        data = self.get_form_data()
        data.setlist("tag-newtag", ["baz"])

        r = self.form(data=data, user=self.user).save().versions.get()

        self.assertEqual([t.name for t in r.tags.all()], ["baz"])


    def test_new_tag_requires_manage_tags_permission(self):
        """Cannot add new tag without correct permission."""
        data = self.get_form_data()
        data.setlist("tag-newtag", ["baz"])

        form = self.form(data=data)

        self.assertEqual(
            form.errors["__all__"],
            ["You do not have permission to create new tags."]
        )


