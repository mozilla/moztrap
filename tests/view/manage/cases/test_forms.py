"""
Tests for case management forms.

"""
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.utils.datastructures import MultiValueDict

from moztrap import model
from tests import case



class AddCaseFormTest(case.DBTestCase):
    """Tests for add-case form."""
    def setUp(self):
        """All add-case tests require at least one product version."""
        self.productversion = self.F.ProductVersionFactory.create(version="1.0")
        self.product = self.productversion.product


    @property
    def user(self):
        """A lazily-created user."""
        if not hasattr(self, "_user"):
            self._user = self.F.UserFactory.create()
        return self._user


    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.cases.forms import AddCaseForm
        return AddCaseForm


    def get_form_data(self):
        defaults = {
            "product": [self.product.id],
            "productversion": [self.productversion.id],
            "idprefix": ["pref"],
            "name": ["Can register."],
            "description": ["A user can sign up for the site."],
            "steps-TOTAL_FORMS": [1],
            "steps-INITIAL_FORMS": [0],
            "steps-0-instruction": ["Fill in form and submit."],
            "steps-0-expected": ["You should get a welcome email."],
            "status": ["active"],
            }
        return MultiValueDict(defaults)


    def test_product_id(self):
        """Product choices render data-product-id attr."""
        html = unicode(self.form()["product"])

        self.assertIn('data-product-id="{0}"'.format(self.product.id), html)


    def test_productversion_product_id(self):
        """Product version choices render data-product-id attr."""
        html = unicode(self.form()["productversion"])

        self.assertIn('data-product-id="{0}"'.format(self.product.id), html)


    def test_success(self):
        """Can add a test case."""
        form = self.form(data=self.get_form_data())

        cv = form.save().versions.get()

        self.assertEqual(cv.name, "Can register.")


    def test_created_by(self):
        """If user is provided, created objects have created_by set."""
        form = self.form(data=self.get_form_data(), user=self.user)

        cv = form.save().versions.get()

        self.assertEqual(cv.case.created_by, self.user)
        self.assertEqual(cv.created_by, self.user)
        self.assertEqual(cv.steps.get().created_by, self.user)


    def test_initial_state(self):
        """New cases should default to active state."""
        form = self.form()

        self.assertEqual(form["status"].value(), "active")


    def test_wrong_product_version(self):
        """Selecting version of wrong product results in validation error."""
        data = self.get_form_data()
        data["product"] = self.F.ProductFactory.create().id

        form = self.form(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {'__all__': [u'Must select a version of the correct product.']}
            )


    def test_no_suite(self):
        """If no manage-suite-cases perm, no suite field."""
        self.assertNotIn("initial", self.form().fields)


    def test_suite(self):
        """Can pick an initial suite for case to be in (with right perms)."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_suite_cases"))
        suite = self.F.SuiteFactory.create(product=self.product)

        data = self.get_form_data()
        data["suite"] = suite.id

        case = self.form(data=data, user=self.user).save()

        self.assertEqual(list(case.suites.all()), [suite])


    def test_initial_suite_order(self):
        """Adding a new case to a suite adds it in last place for the suite"""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_suite_cases"))
        suite = self.F.SuiteFactory.create(product=self.product)
        c1 = self.F.CaseFactory()
        c2 = self.F.CaseFactory()
        self.F.SuiteCaseFactory(
            suite=suite,
            case=c1,
            order=0)
        self.F.SuiteCaseFactory(
            suite=suite,
            case=c2,
            order=1)

        data = self.get_form_data()
        data["suite"] = suite.id

        newcase = self.form(data=data, user=self.user).save()

        self.assertEqual(list(newcase.suites.all()), [suite])

        self.assertEqual(
            [x.case for x in suite.cases.through.objects.order_by("order")],
            [c1, c2, newcase])


    def test_wrong_suite_product(self):
        """Selecting suite from wrong product results in validation error."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_suite_cases"))
        suite = self.F.SuiteFactory.create()  # some other product

        data = self.get_form_data()
        data["suite"] = suite.id

        form = self.form(data=data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {"__all__": [u"Must select a suite for the correct product."]}
            )


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

        caseversion = self.form(data=data).save().versions.get()

        self.assertEqual(list(caseversion.tags.all()), [t1, t2])


    def test_new_tag(self):
        """Can create a new case with a new tag, with correct perm."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_tags"))
        data = self.get_form_data()
        data.setlist("tag-newtag", ["baz"])

        caseversion = self.form(data=data, user=self.user).save().versions.get()

        self.assertEqual([t.name for t in caseversion.tags.all()], ["baz"])


    def test_new_tag_requires_manage_tags_permission(self):
        """Cannot add new tag without correct permission."""
        data = self.get_form_data()
        data.setlist("tag-newtag", ["baz"])

        form = self.form(data=data)

        self.assertEqual(
            form.errors["__all__"],
            ["You do not have permission to create new tags."]
            )


    def test_data_allow_new(self):
        """add_tag field has data-allow-new set true with manage_tags perm."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_tags"))

        form = self.form(user=self.user)

        self.assertEqual(
            form.fields["add_tags"].widget.attrs["data-allow-new"], "true")


    def test_no_allow_new(self):
        """add_tag field has data-allow-new false without manage_tags perm."""
        form = self.form(user=self.user)

        self.assertEqual(
            form.fields["add_tags"].widget.attrs["data-allow-new"], "false")


    def test_attachment(self):
        """Can add an attachment to the new case."""
        files = MultiValueDict(
            {"add_attachment": [SimpleUploadedFile("name.txt", "contents")]}
            )

        caseversion = self.form(
            data=self.get_form_data(), files=files).save().versions.get()

        self.assertEqual(len(caseversion.attachments.all()), 1)


    def test_and_later_versions(self):
        """Can add multiple versions of a test case at once."""
        self.F.ProductVersionFactory.create(
            product=self.product, version="0.5")
        newer_version = self.F.ProductVersionFactory.create(
            product=self.product, version="1.1")

        # these versions from a different product should not be included
        other_product = self.F.ProductFactory.create(name="Other Product")
        self.F.ProductVersionFactory.create(version="2", product=other_product)
        self.F.ProductVersionFactory.create(version="3", product=other_product)
        self.F.ProductVersionFactory.create(version="4", product=other_product)

        data = self.get_form_data()
        data["and_later_versions"] = 1

        case = self.form(data=data).save()

        self.assertEqual(
            [v.productversion for v in case.versions.all()],
            [self.productversion, newer_version]
            )



class AddBulkCasesFormTest(case.DBTestCase):
    """Tests for add-bulk-case form."""
    def setUp(self):
        """All add-bulk-case tests require at least one product version."""
        self.productversion = self.F.ProductVersionFactory.create(version="1.0")
        self.product = self.productversion.product


    @property
    def user(self):
        """A lazily-created user."""
        if not hasattr(self, "_user"):
            self._user = self.F.UserFactory.create()
        return self._user


    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.cases.forms import AddBulkCaseForm
        return AddBulkCaseForm


    def get_form_data(self):
        defaults = {
            "product": [self.product.id],
            "productversion": [self.productversion.id],
            "cases": [
                "Test that I can register\n"
                "this is the description\n"
                "when I fill in form and submit\n"
                "then I get a welcome email\n"
                ],
            "status": ["active"],
            }
        return MultiValueDict(defaults)


    def test_success(self):
        """Can add a test case."""
        form = self.form(data=self.get_form_data())

        cv = form.save()[0].versions.get()

        self.assertEqual(cv.name, "Test that I can register")
        self.assertEqual(cv.case.product, self.product)
        self.assertEqual(cv.productversion, self.productversion)
        self.assertEqual(cv.description, "this is the description")
        self.assertEqual(
            [(s.instruction, s.expected) for s in cv.steps.all()],
            [("when I fill in form and submit", "then I get a welcome email")]
            )
        self.assertEqual(cv.status, "active")


    def test_parse_error(self):
        """Error in bulk case text parsing."""
        data = self.get_form_data()
        data["cases"] = "Foo"

        form = self.form(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["cases"], [u"Expected 'Test that ...', not 'Foo'"])


    def test_created_by(self):
        """If user is provided, created objects have created_by set."""
        form = self.form(data=self.get_form_data(), user=self.user)

        cv = form.save()[0].versions.get()

        self.assertEqual(cv.case.created_by, self.user)
        self.assertEqual(cv.created_by, self.user)
        self.assertEqual(cv.steps.get().created_by, self.user)


    def test_wrong_product_version(self):
        """Selecting version of wrong product results in validation error."""
        data = self.get_form_data()
        data["product"] = self.F.ProductFactory.create().id

        form = self.form(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {'__all__': [u'Must select a version of the correct product.']}
            )


    def test_no_suite(self):
        """If no manage-suite-cases perm, no suite field."""
        self.assertNotIn("suite", self.form().fields)


    def test_suite(self):
        """Can pick an initial suite for case to be in (with right perms)."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_suite_cases"))
        suite = self.F.SuiteFactory.create(product=self.product)

        data = self.get_form_data()
        data["suite"] = suite.id

        case = self.form(data=data, user=self.user).save()[0]

        self.assertEqual(list(case.suites.all()), [suite])


    def test_initial_suite_order(self):
        """Adding a new case to a suite adds it in last place for the suite"""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_suite_cases"))
        suite = self.F.SuiteFactory.create(product=self.product)
        c1 = self.F.CaseFactory()
        c2 = self.F.CaseFactory()
        self.F.SuiteCaseFactory(
            suite=suite,
            case=c1,
            order=0)
        self.F.SuiteCaseFactory(
            suite=suite,
            case=c2,
            order=1)

        data = self.get_form_data()
        data["suite"] = suite.id

        newcase = self.form(data=data, user=self.user).save()[0]

        self.assertEqual(list(newcase.suites.all()), [suite])

        self.assertEqual(
            [x.case for x in suite.cases.through.objects.order_by("order")],
            [c1, c2, newcase])


    def test_wrong_suite_product(self):
        """Selecting suite from wrong product results in validation error."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_suite_cases"))
        suite = self.F.SuiteFactory.create()  # some other product

        data = self.get_form_data()
        data["suite"] = suite.id

        form = self.form(data=data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {"__all__": [u"Must select a suite for the correct product."]}
            )


    def test_tag(self):
        """Can tag a new case with some existing tags."""
        t1 = self.F.TagFactory.create(name="foo")
        t2 = self.F.TagFactory.create(name="bar")
        data = self.get_form_data()
        data.setlist("tag-tag", [t1.id, t2.id])

        caseversion = self.form(data=data).save()[0].versions.get()

        self.assertEqual(list(caseversion.tags.all()), [t1, t2])


    def test_new_tag(self):
        """Can create a new case with a new tag, with correct perm."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_tags"))
        data = self.get_form_data()
        data.setlist("tag-newtag", ["baz"])

        caseversion = self.form(data=data, user=self.user).save(
            )[0].versions.get()

        self.assertEqual([t.name for t in caseversion.tags.all()], ["baz"])


    def test_new_tag_requires_manage_tags_permission(self):
        """Cannot add new tag without correct permission."""
        data = self.get_form_data()
        data.setlist("tag-newtag", ["baz"])

        form = self.form(data=data)

        self.assertEqual(
            form.errors["__all__"],
            ["You do not have permission to create new tags."]
            )


    def test_data_allow_new(self):
        """add_tag field has data-allow-new set true with manage_tags perm."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_tags"))

        form = self.form(user=self.user)

        self.assertEqual(
            form.fields["add_tags"].widget.attrs["data-allow-new"], "true")


    def test_no_allow_new(self):
        """add_tag field has data-allow-new false without manage_tags perm."""
        form = self.form(user=self.user)

        self.assertEqual(
            form.fields["add_tags"].widget.attrs["data-allow-new"], "false")


    def test_and_later_versions(self):
        """Can add multiple versions of a test case at once."""
        self.F.ProductVersionFactory.create(
            product=self.product, version="0.5")
        newer_version = self.F.ProductVersionFactory.create(
            product=self.product, version="1.1")

        # these versions from a different product should not be included
        other_product = self.F.ProductFactory.create(name="Other Product")
        self.F.ProductVersionFactory.create(version="2", product=other_product)
        self.F.ProductVersionFactory.create(version="3", product=other_product)
        self.F.ProductVersionFactory.create(version="4", product=other_product)

        data = self.get_form_data()
        data["and_later_versions"] = 1

        case = self.form(data=data).save()[0]

        self.assertEqual(
            [v.productversion for v in case.versions.all()],
            [self.productversion, newer_version]
            )



class EditCaseVersionFormTest(case.DBTestCase):
    """Tests for EditCaseVersionForm."""
    @property
    def user(self):
        """A lazily-created user."""
        if not hasattr(self, "_user"):
            self._user = self.F.UserFactory.create()
        return self._user


    @property
    def form(self):
        """The form class under test."""
        from moztrap.view.manage.cases.forms import EditCaseVersionForm
        return EditCaseVersionForm


    def test_initial(self):
        """Initial data is populated accurately."""
        cv = self.F.CaseVersionFactory.create(
            case__idprefix="pref",
            name="a name",
            description="a desc",
            status="active",
            )
        self.F.CaseStepFactory.create(
            caseversion=cv, instruction="do this", expected="see that")

        form = self.form(instance=cv)

        self.assertEqual(
            form.initial,
            {
                "name": "a name",
                "description": "a desc",
                "idprefix": "pref",
                "status": "active",
                "cc_version": cv.cc_version,
                }
            )
        self.assertEqual(
            form.steps_formset.forms[0].initial,
            {
                "caseversion": cv.id,
                "instruction": "do this",
                "expected": "see that",
                }
            )


    def test_save_edits(self):
        """Can edit basic data and steps and save."""
        cv = self.F.CaseVersionFactory.create(
            name="a name", description="a desc", status="draft")
        step = self.F.CaseStepFactory.create(
            caseversion=cv, instruction="do this", expected="see that")

        form = self.form(
            instance=cv,
            data=MultiValueDict(
                {
                    "name": ["new name"],
                    "description": ["new desc"],
                    "idprefix": ["pref"],
                    "status": ["active"],
                    "cc_version": str(cv.cc_version),
                    "steps-TOTAL_FORMS": ["2"],
                    "steps-INITIAL_FORMS": ["1"],
                    "steps-0-id": [""],
                    "steps-0-instruction": ["new step"],
                    "steps-0-expected": [""],
                    "steps-1-id": [str(step.id)],
                    "steps-1-instruction": ["do this instead"],
                    "steps-1-expected": [""],
                    }
                )
            )

        cv = form.save()
        cv = self.refresh(cv)

        self.assertEqual(cv.name, "new name")
        self.assertEqual(cv.description, "new desc")
        self.assertEqual(cv.status, "active")
        self.assertEqual(
            [s.instruction for s in cv.steps.all()],
            ["new step", "do this instead"])


    def test_save_tags(self):
        """Can add/remove tags."""
        self.user.user_permissions.add(
            model.Permission.objects.get(codename="manage_tags"))

        cv = self.F.CaseVersionFactory.create()

        t1 = self.F.TagFactory.create(name="one")
        t2 = self.F.TagFactory.create(name="two")
        t3 = self.F.TagFactory.create(name="three")

        cv.tags.add(t1, t2)

        form = self.form(
            instance=cv,
            user=self.user,
            data=MultiValueDict(
                {
                    "name": ["new name"],
                    "description": ["new desc"],
                    "status": ["active"],
                    "cc_version": str(cv.cc_version),
                    "tag-tag": [t2.id, t3.id],
                    "tag-newtag": ["foo"],
                    "steps-TOTAL_FORMS": ["0"],
                    "steps-INITIAL_FORMS": ["0"],
                    }
                )
            )

        cv = form.save()

        self.assertEqual(
            set([t.name for t in cv.tags.all()]),
            set(["two", "three", "foo"])
            )


    def test_save_attachments(self):
        """Can add/remove attachments."""

        cv = self.F.CaseVersionFactory.create()

        a1 = self.F.CaseAttachmentFactory.create(
            caseversion=cv, name="Foo1")
        self.F.CaseAttachmentFactory.create(
            caseversion=cv, name="Foo2")

        form = self.form(
            instance=cv,
            user=self.user,
            data=MultiValueDict(
                {
                    "name": ["new name"],
                    "description": ["new desc"],
                    "status": ["active"],
                    "cc_version": [str(cv.cc_version)],
                    "remove-attachment": [str(a1.id)],
                    "steps-TOTAL_FORMS": ["0"],
                    "steps-INITIAL_FORMS": ["0"],
                    }
                ),
            files=MultiValueDict(
                {"add_attachment": [SimpleUploadedFile("Foo3", "contents")]})
            )

        cv = form.save()

        self.assertEqual(
            set([ca.name for ca in cv.attachments.all()]),
            set(["Foo2", "Foo3"])
            )


    def test_concurrent_save(self):
        """Saving edits to out-of-date version returns None and sets error."""
        cv = self.F.CaseVersionFactory.create(
            name="a name", description="a desc", status="draft")
        submitted_version = cv.cc_version
        cv.save()  # increments the concurrency-control version

        form = self.form(
            instance=cv,
            data=MultiValueDict(
                {
                    "name": ["new name"],
                    "description": ["new desc"],
                    "status": ["active"],
                    "cc_version": str(submitted_version),
                    "steps-TOTAL_FORMS": ["0"],
                    "steps-INITIAL_FORMS": ["0"],
                    }
                )
            )

        self.assertIsNone(form.save_if_valid())
        self.assertIn("Another user saved changes", form.errors["__all__"][0])



class StepFormSetTest(case.DBTestCase):
    """Tests for StepFormSet."""
    @property
    def formset(self):
        """The class under test."""
        from moztrap.view.manage.cases.forms import StepFormSet
        return StepFormSet


    def bound(self, data, instance=None):
        """Return a formset, with instance, bound to data."""
        if instance is None:
            instance = self.F.CaseVersionFactory.create()
        return self.formset(data=data, instance=instance)


    def assertSteps(self, caseversion, steps):
        """Assert ``caseversion`` has ``steps``, as (inst, exp) tuples."""
        self.assertEqual(
            [(s.instruction, s.expected) for s in caseversion.steps.all()],
            steps)


    def test_existing(self):
        """Displays forms for existing steps when unbound."""
        step = self.F.CaseStepFactory.create(instruction="do this")
        fs = self.formset(instance=step.caseversion)

        self.assertEqual(len(fs), 1)
        self.assertEqual(list(fs)[0].initial["instruction"], "do this")


    def test_add_new(self):
        """Can add new steps."""
        fs = self.bound(
            {
                "steps-TOTAL_FORMS": "1",
                "steps-INITIAL_FORMS": "0",
                "steps-0-id": "",
                "steps-0-instruction": "do this",
                "steps-0-expected": "see that",
                }
            )
        fs.save()

        self.assertSteps(fs.instance, [("do this", "see that")])


    def test_unknown_id_adds_new(self):
        """Unknown step id just creates a new step."""
        fs = self.bound(
            {
                "steps-TOTAL_FORMS": "1",
                "steps-INITIAL_FORMS": "0",
                "steps-0-id": "27",
                "steps-0-instruction": "do this",
                "steps-0-expected": "see that",
                }
            )
        fs.save()

        self.assertSteps(fs.instance, [("do this", "see that")])


    def test_bad_id_adds_new(self):
        """Unknown step id just creates a new step."""
        fs = self.bound(
            {
                "steps-TOTAL_FORMS": "1",
                "steps-INITIAL_FORMS": "0",
                "steps-0-id": "foo",
                "steps-0-instruction": "do this",
                "steps-0-expected": "see that",
                }
            )
        fs.save()

        self.assertSteps(fs.instance, [("do this", "see that")])


    def test_edit_existing(self):
        """Can edit existing steps."""
        step = self.F.CaseStepFactory.create()
        fs = self.bound(
            {
                "steps-TOTAL_FORMS": "1",
                "steps-INITIAL_FORMS": "1",
                "steps-0-id": str(step.id),
                "steps-0-instruction": "do this",
                "steps-0-expected": "see that",
                },
            instance=step.caseversion,
            )
        fs.save()

        self.assertSteps(fs.instance, [("do this", "see that")])


    def test_delete_existing(self):
        """Can delete existing steps."""
        step = self.F.CaseStepFactory.create()
        fs = self.bound(
            {
                "steps-TOTAL_FORMS": "0",
                "steps-INITIAL_FORMS": "1",  # JS doesn't touch this
                },
            instance=step.caseversion,
            )
        fs.save()

        self.assertSteps(fs.instance, [])


    def test_delete_existing_and_add_new(self):
        """Can delete an existing step and put a new one in its place."""
        step = self.F.CaseStepFactory.create()
        fs = self.bound(
            {
                "steps-TOTAL_FORMS": "1",
                "steps-INITIAL_FORMS": "1",  # JS doesn't touch this
                "steps-0-id": "",
                "steps-0-instruction": "do this",
                "steps-0-expected": "see that",
                },
            instance=step.caseversion,
            )
        fs.save()

        self.assertSteps(fs.instance, [("do this", "see that")])


    def test_intersperse_new(self):
        """Can add a new step in between existing ones."""
        step1 = self.F.CaseStepFactory.create(instruction="one")
        step2 = self.F.CaseStepFactory.create(
            instruction="two", caseversion=step1.caseversion)
        fs = self.bound(
            {
                "steps-TOTAL_FORMS": "3",
                "steps-INITIAL_FORMS": "2",
                "steps-0-id": str(step1.id),
                "steps-0-instruction": "one",
                "steps-0-expected": "",
                "steps-1-id": "",
                "steps-1-instruction": "new",
                "steps-1-expected": "",
                "steps-2-id": str(step2.id),
                "steps-2-instruction": "three",
                "steps-2-expected": "",
                },
            instance=step1.caseversion,
            )
        fs.save()

        self.assertSteps(fs.instance, [("one", ""), ("new", ""), ("three", "")])


    def test_marks_created_by(self):
        """Steps are saved with created-by data."""
        u = self.F.UserFactory.create()
        fs = self.bound(
            {
                "steps-TOTAL_FORMS": "1",
                "steps-INITIAL_FORMS": "0",
                "steps-0-id": "",
                "steps-0-instruction": "do this",
                "steps-0-expected": "see that",
                },
            )
        fs.save(user=u)

        self.assertEqual(fs.instance.steps.get().created_by, u)


    def test_marks_modified_by(self):
        """Steps are saved with modified-by data."""
        u = self.F.UserFactory.create()
        step = self.F.CaseStepFactory.create()
        fs = self.bound(
            {
                "steps-TOTAL_FORMS": "1",
                "steps-INITIAL_FORMS": "1",
                "steps-0-id": str(step.id),
                "steps-0-instruction": "do this",
                "steps-0-expected": "see that",
                },
            instance=step.caseversion,
            )
        fs.save(user=u)

        self.assertEqual(self.refresh(step).modified_by, u)
