"""
Tests for MozTrap form utilities.

"""
from django import forms

from tests import case



class MTFormsTestCase(case.DBTestCase):
    """Base test case class for mtforms tests."""
    @property
    def mtforms(self):
        """The module under test."""
        from moztrap.view.utils import mtforms
        return mtforms



class TestNonFieldErrorsClassFormMixin(MTFormsTestCase):
    """Tests for NonFieldErrorsClassMixin."""
    @property
    def form(self):
        """A sample descended form class."""
        class PersonForm(self.mtforms.NonFieldErrorsClassFormMixin, forms.Form):
            name = forms.CharField()
            age = forms.IntegerField()

            def clean(self):
                if (self.cleaned_data.get("name") == "Shakespeare" and
                    self.cleaned_data.get("age", 0) < 400):
                    raise forms.ValidationError("Too young to be Shakespeare.")

        return PersonForm


    def test_non_field_errorlist(self):
        """Non-field-error list has nonfield class."""
        form = self.form({"name": "Shakespeare", "age": "25"})

        nfe = form.non_field_errors()

        self.assertTrue('class="errorlist nonfield"' in unicode(nfe))


    def test_field_errorlist(self):
        """Field error list does not have nonfield class."""
        form = self.form({"name": "Joe"})

        fe = unicode(form["age"].errors)

        self.assertTrue('class="' in fe)
        self.assertFalse("nonfield" in fe)


    def test_no_nonfield_errors(self):
        """Works if there are no nonfield errors."""
        form = self.form({"name": "Joe", "age": "25"})

        self.assertEqual(unicode(form.non_field_errors()), u"")



class BareTextareaTest(MTFormsTestCase):
    """Tests for BareTextarea."""
    def test_no_attrs(self):
        """BareTextarea does not have rows or cols attributes."""
        self.assertEqual(self.mtforms.BareTextarea().attrs, {})



class ProductIdAttrsTest(MTFormsTestCase):
    """Tests for product_id_attrs."""
    def test_product_id_attr(self):
        """Returns dict with data-product-id."""
        pv = self.F.ProductVersionFactory.create()
        self.assertEqual(
            self.mtforms.product_id_attrs(pv),
            {"data-product-id": pv.product.id},
            )



class MTModelFormTest(MTFormsTestCase):
    """Tests for MTModelForm."""
    def setUp(self):
        """Setup for MTModelForm tests; create a user."""
        self.user = self.F.UserFactory.create()


    @property
    def form(self):
        """A sample descended form class."""
        class ProductForm(self.mtforms.MTModelForm):
            """Sample MTModelForm"""
            class Meta:
                model = self.model.Product
                fields = ["name"]

        return ProductForm


    def test_new_instance_records_created_by(self):
        """Adding a new instance records the created_by user."""
        f = self.form({"name": "Foo", "cc_version": "0"}, user=self.user)

        product = f.save()

        self.assertEqual(product.created_by, self.user)


    def test_edited_instance_records_modified_by(self):
        """Editing an instance records the modified_by user."""
        p = self.F.ProductFactory.create()
        f = self.form(
            {"name": "Foo", "cc_version": str(p.cc_version)},
            instance=p,
            user=self.user,
            )

        product = f.save()

        self.assertEqual(product.modified_by, self.user)


    def test_commit_false_records_modified_by(self):
        """modified_by user is still recorded even with commit=False."""
        f = self.form({"name": "Foo", "cc_version": "0"})

        product = f.save(commit=False, user=self.user)

        product.save()

        self.assertEqual(product.modified_by, self.user)


    def test_commit_false_allows_user_to_be_passed_in_later(self):
        """With commit=False, user can be passed in at later save."""
        u = self.F.UserFactory.create()
        f = self.form({"name": "Foo", "cc_version": "0"})

        product = f.save(commit=False, user=u)

        product.save(user=self.user)

        self.assertEqual(product.modified_by, self.user)


    def test_save_concurrent(self):
        """save will raise ConcurrencyError if there was a concurrent edit."""
        p = self.F.ProductFactory.create()
        submitted_version = p.cc_version
        p.name = "Foo"
        p.save()

        f = self.form(
            {"name": "New", "cc_version": str(submitted_version)},
            instance=p,
            )

        with self.assertRaises(self.model.ConcurrencyError):
            f.save()


    def test_save_if_valid_not_valid(self):
        """save_if_valid returns None if there are errors."""
        f = self.form({"name": "", "cc_version": "0"})

        self.assertIsNone(f.save_if_valid())
        self.assertEqual(f.errors, {"name": [u"This field is required."]})
        self.assertEqual(self.model.Product.objects.count(), 0)


    def test_save_if_valid_concurrent(self):
        """
        save_if_valid adds an error message on a concurrent edit.

        This tests the case where the concurrent edit happened before this form
        was submitted at all. So the model instance fetched and passed to the
        form is actually up to date, but the submitted form data contains an
        older ``cc_version``.

        """
        p = self.F.ProductFactory.create()
        submitted_version = p.cc_version
        p.name = "Foo"
        p.save()

        f = self.form(
            {"name": "New", "cc_version": str(submitted_version)},
            instance=p,
            )

        self.assertIsNone(f.save_if_valid())
        self.assertEqual(
            f.errors,
            {
                "__all__": [
                    u"Another user saved changes to this object in the "
                    u'meantime. Please <a href="">review their changes</a> '
                    u"and save yours again if they still apply."
                    ]
                }
            )
        # Added error uses proper error list class
        self.assertIsInstance(f.errors["__all__"], f.error_class)


    def test_save_if_valid_redisplay_updates_version(self):
        """
        On a concurrency error, redisplayed form can be successfully submitted.

        Rather than redisplaying the form with the known-to-be-out-of-date
        version, we redisplay it with the updated version.

        Need to pass in a QueryDict here, as immutability is relevant.

        """
        p = self.F.ProductFactory.create()
        submitted_version = p.cc_version
        p.name = "Foo"
        p.save()

        f = self.form(
            {"name": "New", "cc_version": str(submitted_version)},
            instance=p,
            )

        self.assertIsNone(f.save_if_valid())
        self.assertEqual(f["cc_version"].value(), p.cc_version)


    def test_save_if_valid_race_redisplay_updates_version(self):
        """On a race concurrency error, redisplayed form can be submitted."""
        p = self.F.ProductFactory.create()

        p2 = self.model.Product.objects.get()
        p2.name = "Foo"
        p2.save()

        from django.http import QueryDict
        f = self.form(
            QueryDict("name=New&cc_version={0}".format(p.cc_version)),
            instance=p,
            )

        self.assertIsNone(f.save_if_valid())
        self.assertEqual(f["cc_version"].value(), p2.cc_version)


    def test_save_if_valid_concurrent_race(self):
        """
        save_if_valid adds an error message on a rare race-condition edit.

        This tests the much less common situation where the concurrent edit is
        actually saved to the database in between the fetching of the form's
        instance and the validation of the form, so both the form's instance
        and the submitted data have an out-of-date version.

        """
        p = self.F.ProductFactory.create()

        p2 = self.model.Product.objects.get()
        p2.name = "Foo"
        p2.save()

        f = self.form({"name": "New", "cc_version": str(p.cc_version)}, instance=p)

        self.assertIsNone(f.save_if_valid())
        self.assertEqual(
            f.errors,
            {
                "__all__": [
                    u"Another user saved changes to this object in the "
                    u'meantime. Please <a href="">review their changes</a> '
                    u"and save yours again if they still apply."
                    ]
                }
            )


    def test_save_if_valid_success(self):
        """save_if_valid saves and returns the object on success."""
        p = self.F.ProductFactory.create()
        submitted_version = p.cc_version

        f = self.form(
            {"name": "New", "cc_version": str(submitted_version)},
            instance=p,
            )

        product = f.save_if_valid()

        self.assertEqual(product, p)
        self.assertEqual(product.name, "New")
        self.assertEqual(f.errors, {})


    def test_save_if_valid_accepts_user(self):
        """save_if_valid accepts current user and saves with it."""
        p = self.F.ProductFactory.create()
        u = self.F.UserFactory.create()
        submitted_version = p.cc_version

        f = self.form(
            {"name": "New", "cc_version": str(submitted_version)},
            instance=p,
            )

        product = f.save_if_valid(user=u)

        self.assertEqual(product.modified_by, u)


    def test_save_if_valid_respects_init_user(self):
        """save_if_valid uses user passed in on form instantiation."""
        p = self.F.ProductFactory.create()
        u = self.F.UserFactory.create()
        submitted_version = p.cc_version

        f = self.form(
            {"name": "New", "cc_version": str(submitted_version)},
            instance=p,
            user=u,
            )

        product = f.save_if_valid()

        self.assertEqual(product.modified_by, u)


    def test_cc_version_default(self):
        """With no instance, cc_version field defaults to 0."""
        f = self.form()

        self.assertEqual(f["cc_version"].value(), 0)


    def test_cc_version_initial(self):
        """With an instance, cc_version initial value is from instance."""
        p = self.F.ProductFactory.create()
        p.save()  # make the version nonzero

        f = self.form(instance=p)

        self.assertEqual(f["cc_version"].value(), p.cc_version)


    def test_cc_version_hidden(self):
        """cc_version field renders as a hidden input."""
        f = self.form()

        self.assertIn("hidden", unicode(f["cc_version"]))



class MTModelChoiceFieldTest(MTFormsTestCase):
    """Tests for MTModelChoiceField."""
    @property
    def form(self):
        """A sample form using the field class under test."""
        class ProductVersionForm(forms.Form):
            """Sample form using MTModelChoiceField."""
            product = self.mtforms.MTModelChoiceField(
                self.model.Product.objects.all(),
                label_from_instance=lambda p: "FooLabel {0}".format(unicode(p)),
                choice_attrs=lambda p: {"data-product-id": p.id}
                )
            product2 = self.mtforms.MTModelChoiceField(
                self.model.Product.objects.all())

        return ProductVersionForm


    def test_label_from_instance(self):
        """Custom label_from_instance callable is used."""
        self.F.ProductFactory(name="Bar")
        s = unicode(self.form()["product"])

        self.assertIn(">FooLabel Bar<", s, s)


    def test_default_label_from_instance(self):
        """Default label_from_instance is unicode of instance."""
        self.F.ProductFactory(name="Bar")
        s = unicode(self.form()["product2"])

        self.assertIn(">Bar<", s, s)


    def test_choice_attrs(self):
        """Custom choice_attrs callable is used."""
        p = self.F.ProductFactory(name="Bar")
        s = unicode(self.form()["product"])

        self.assertIn('data-product-id="{0}"'.format(p.id), s, s)


    def test_set_choices(self):
        """Can set choices explicitly."""
        f = self.form()
        f.fields["product"].choices = [(1, "Foo")]
        s = unicode(f["product"])

        self.assertEqual(f.fields["product"].choices, [(1, "Foo")])
        self.assertIn(">Foo<", s, s)



class AutocompleteInputTest(MTFormsTestCase):
    """Tests for AutocompleteInput."""
    def test_autocomplete_off(self):
        """Sets autocomplete attr to "off" to disable browser autocomplete."""
        self.assertIn(
            'autocomplete="off"',
            self.mtforms.AutocompleteInput(url="foo").render("n", "")
            )


    def test_autocomplete_url(self):
        """Sets data-autocomplete-url."""
        self.assertIn(
            'data-autocomplete-url="/foo/bar/"',
            self.mtforms.AutocompleteInput(url="/foo/bar/").render("n", "")
            )


    def test_autocomplete_url_callable(self):
        """Sets data-autocomplete-url from callable url argument."""
        self.assertIn(
            'data-autocomplete-url="/foo/bar/"',
            self.mtforms.AutocompleteInput(
                url=lambda: "/foo/bar/").render("n", "")
            )



class FilteredSelectMultipleTest(MTFormsTestCase):
    """Tests for FilteredSelectMultiple."""
    def test_override_choice_template(self):
        """Can override choice_template in context at initialization."""
        fsm = self.mtforms.FilteredSelectMultiple(choice_template="foo")

        self.assertEqual(fsm.get_context_data()["choice_template"], "foo")


    def test_override_listordering_template(self):
        """Can override listordering_template in context at initialization."""
        fsm = self.mtforms.FilteredSelectMultiple(listordering_template="foo")

        self.assertEqual(fsm.get_context_data()["listordering_template"], "foo")
