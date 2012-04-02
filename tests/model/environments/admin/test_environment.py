"""
Tests for Environment admin.

"""
from mock import patch

from tests import case



class EnvironmentAdminTest(case.admin.AdminTestCase):
    app_label = "environments"
    model_name = "environment"


    def test_changelist(self):
        """Environment changelist page loads without error, contains name."""
        self.F.EnvironmentFactory.create_full_set({"OS": ["Linux"]})

        self.get(self.changelist_url).mustcontain("Linux")


    def test_change_page(self):
        """Environment change page loads without error, contains name."""
        e = self.F.EnvironmentFactory.create_full_set({"OS": ["Linux"]})[0]

        self.get(self.change_url(e)).mustcontain("Linux")


    def test_change_page_element(self):
        """Environment change page includes Element-m2m inline."""
        e = self.F.EnvironmentFactory.create_full_set({"OS": ["Linux"]})[0]

        self.get(self.change_url(e)).mustcontain("Linux")


    def test_add_element_m2m_with_environment(self):
        """Can add elements when creating a new Environment"""
        profile = self.F.ProfileFactory.create()
        element = self.F.ElementFactory.create(name="Linux")

        # patching extra avoids need for JS to add element-m2m
        with patch(
            "moztrap.model.environments.admin.EnvironmentElementInline.extra", 1):

            form = self.get(self.add_url).forms[0]
            form["profile"] = str(profile.id)
            form["Environment_elements-0-element"] = str(element.id)
            res = form.submit()

        self.assertEqual(res.status_int, 302)

        self.assertEqual(
            profile.environments.get(
                ).elements.get().name, "Linux")
