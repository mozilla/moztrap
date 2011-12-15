from .base import AdminTestCase

from ..library.builders import create_case, create_caseversion


class CaseAdminTest(AdminTestCase):
    app_label = "library"
    model_name = "case"


    def test_changelist(self):
        """Case changelist page loads without error, contains id."""
        c = create_case()

        self.get(self.changelist_url).mustcontain(c.id)


    def test_change(self):
        """Case change page loads without error, contains id."""
        c = create_case()

        self.get(self.change_url(c)).mustcontain(c.id)


    def test_change_version(self):
        """Case change page includes CaseVersion inline."""
        cv = create_caseversion(name="Can load a website")

        self.get(self.change_url(cv.case)).mustcontain(
            "Can load a website")
