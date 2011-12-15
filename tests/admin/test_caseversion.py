from .base import AdminTestCase

from ..library.builders import create_caseversion, create_casestep



class CaseVersionAdminTest(AdminTestCase):
    app_label = "library"
    model_name = "caseversion"


    def test_changelist(self):
        """CaseVersion changelist page loads without error, contains name."""
        create_caseversion(name="Can load a website")

        self.get(self.changelist_url).mustcontain("Can load a website")


    def test_change(self):
        """CaseVersion change page loads without error, contains name."""
        p = create_caseversion(name="Can load a website")

        self.get(self.change_url(p)).mustcontain("Can load a website")


    def test_change_step(self):
        """CaseVersion change page includes CaseStep inline."""
        s = create_casestep(instruction="Type a URL in the address bar")

        self.get(self.change_url(s.caseversion)).mustcontain(
            "Type a URL in the address bar")
