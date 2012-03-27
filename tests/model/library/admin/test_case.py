"""
Tests for Case admin.

"""
from tests import case



class CaseAdminTest(case.admin.AdminTestCase):
    app_label = "library"
    model_name = "case"


    def test_changelist(self):
        """Case changelist page loads without error, contains id."""
        c = self.F.CaseFactory()

        self.get(self.changelist_url).mustcontain(c.id)


    def test_change_page(self):
        """Case change page loads without error, contains id."""
        c = self.F.CaseFactory()

        self.get(self.change_url(c)).mustcontain(c.id)


    def test_change_page_version(self):
        """Case change page includes CaseVersion inline."""
        cv = self.F.CaseVersionFactory(name="Can load a website")

        self.get(self.change_url(cv.case)).mustcontain(
            "Can load a website")
