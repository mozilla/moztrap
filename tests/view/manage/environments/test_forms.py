"""
Tests for environment forms.

"""
from tests import case



class AddProfileFormTest(case.DBTestCase):
    """Tests for AddProfileForm."""
    @property
    def form(self):
        """The form class under test."""
        from cc.view.manage.environments.forms import AddProfileForm
        return AddProfileForm


    def test_save(self):
        """Given a name and element list, autogenerates a profile."""
        e1 = self.F.ElementFactory.create()
        e2 = self.F.ElementFactory.create()
        self.F.ElementFactory.create()
        u = self.F.UserFactory.create()

        f = self.form(
            {
                "elements": [str(e1.id), str(e2.id)],
                "name": "Foo",
                "cc_version": "0"},
            user=u,
            )
        self.assertTrue(f.is_valid())
        p = f.save()

        self.assertEqual(p.created_by, u)
        self.assertEqual(p.name, "Foo")
        self.assertEqual(
            set(p.environments.get().elements.all()), set([e1, e2]))


    def test_empty_category_rendered(self):
        """A category with no elements is still rendered in elements widget."""
        self.F.CategoryFactory.create(name="EmptyCat")

        self.assertIn("EmptyCat", unicode(self.form()["elements"]))


    def test_elements_rendered(self):
        """Elements are rendered in widget."""
        self.F.ElementFactory.create(name="SomeElement")

        self.assertIn("SomeElement", unicode(self.form()["elements"]))


    def test_selected_element_ids(self):
        """Selected elements are rendered checked."""
        unsel = self.F.ElementFactory.create()
        sel = self.F.ElementFactory.create()

        f = self.form({"elements": [str(sel.id)]})

        rendered = unicode(f["elements"])
        self.assertIn('id="element-{0}">'.format(unsel.id), rendered)
        self.assertIn('id="element-{0}" checked>'.format(sel.id), rendered)
