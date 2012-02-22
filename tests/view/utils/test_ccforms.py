# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for Case Conductor form utilities.

"""
from django import forms

from tests import case



class CCFormsTestCase(case.DBTestCase):
    """Base test case class for ccforms tests."""
    @property
    def ccforms(self):
        """The module under test."""
        from cc.view.utils import ccforms
        return ccforms



class TestNonFieldErrorsClassFormMixin(CCFormsTestCase):
    """Tests for NonFieldErrorsClassMixin."""
    @property
    def form(self):
        """A sample descended form class."""
        class PersonForm(self.ccforms.NonFieldErrorsClassFormMixin, forms.Form):
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



class BareTextareaTest(CCFormsTestCase):
    """Tests for BareTextarea."""
    def test_no_attrs(self):
        """BareTextarea does not have rows or cols attributes."""
        self.assertEqual(self.ccforms.BareTextarea().attrs, {})



class CCModelFormTest(CCFormsTestCase):
    """Tests for CCModelForm."""
    def setUp(self):
        """Setup for CCModelForm tests; create a user."""
        self.user = self.F.UserFactory.create()


    @property
    def form(self):
        """A sample descended form class."""
        class ProductForm(self.ccforms.CCModelForm):
            """Sample CCModelForm"""
            class Meta:
                model = self.model.Product
                fields = ["name"]

        return ProductForm


    def test_new_instance_records_created_by(self):
        """Adding a new instance records the created_by user."""
        f = self.form({"name": "Foo"}, user=self.user)

        product = f.save()

        self.assertEqual(product.created_by, self.user)


    def test_edited_instance_records_modified_by(self):
        """Editing an instance records the modified_by user."""
        p = self.F.ProductFactory.create()
        f = self.form({"name": "Foo"}, instance=p, user=self.user)

        product = f.save()

        self.assertEqual(product.modified_by, self.user)


    def test_commit_false_records_modified_by(self):
        """modified_by user is still recorded even with commit=False."""
        f = self.form({"name": "Foo"})

        product = f.save(commit=False, user=self.user)

        product.save()

        self.assertEqual(product.modified_by, self.user)


    def test_commit_false_allows_user_to_be_passed_in_later(self):
        """With commit=False, user can be passed in at later save."""
        u = self.F.UserFactory.create()
        f = self.form({"name": "Foo"})

        product = f.save(commit=False, user=u)

        product.save(user=self.user)

        self.assertEqual(product.modified_by, self.user)



class CCModelChoiceFieldTest(CCFormsTestCase):
    """Tests for CCModelChoiceField."""
    @property
    def form(self):
        """A sample form using the field class under test."""
        class ProductVersionForm(forms.Form):
            """Sample form using CCModelChoiceField."""
            product = self.ccforms.CCModelChoiceField(
                self.model.Product.objects.all(),
                label_from_instance=lambda p: "FooLabel {0}".format(unicode(p)),
                choice_attrs=lambda p: {"data-product-id": p.id}
                )
            product2 = self.ccforms.CCModelChoiceField(
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



class AutocompleteInputTest(CCFormsTestCase):
    """Tests for AutocompleteInput."""
    def test_autocomplete_off(self):
        """Sets autocomplete attr to "off" to disable browser autocomplete."""
        self.assertIn(
            'autocomplete="off"',
            self.ccforms.AutocompleteInput(url="foo").render("n", "")
            )


    def test_autocomplete_url(self):
        """Sets data-autocomplete-url."""
        self.assertIn(
            'data-autocomplete-url="/foo/bar/"',
            self.ccforms.AutocompleteInput(url="/foo/bar/").render("n", "")
            )


    def test_autocomplete_url_callable(self):
        """Sets data-autocomplete-url from callable url argument."""
        self.assertIn(
            'data-autocomplete-url="/foo/bar/"',
            self.ccforms.AutocompleteInput(
                url=lambda: "/foo/bar/").render("n", "")
            )



class FilteredSelectMultipleTest(CCFormsTestCase):
    """Tests for FilteredSelectMultiple."""
    def test_override_choice_template(self):
        """Can override choice_template in context at initialization."""
        fsm = self.ccforms.FilteredSelectMultiple(choice_template="foo")

        self.assertEqual(fsm.get_context_data()["choice_template"], "foo")


    def test_override_listordering_template(self):
        """Can override listordering_template in context at initialization."""
        fsm = self.ccforms.FilteredSelectMultiple(listordering_template="foo")

        self.assertEqual(fsm.get_context_data()["listordering_template"], "foo")
