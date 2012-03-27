"""
Tests for Category admin.

"""
from tests import case



class CategoryAdminTest(case.admin.AdminTestCase):
    app_label = "environments"
    model_name = "category"


    def test_changelist(self):
        """Category changelist page loads without error, contains name."""
        self.F.CategoryFactory.create(name="Operating System")

        self.get(self.changelist_url).mustcontain("Operating System")


    def test_change_page(self):
        """Category change page loads without error, contains name."""
        s = self.F.CategoryFactory.create(name="Operating System")

        self.get(self.change_url(s)).mustcontain("Operating System")


    def test_change_page_element(self):
        """Category change page includes Element inline."""
        e = self.F.ElementFactory.create(name="Linux")

        self.get(self.change_url(e.category)).mustcontain("Linux")
