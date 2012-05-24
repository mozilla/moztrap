"""
Tests for Result admin.

"""
from tests import case



class ResultAdminTest(case.admin.AdminTestCase):
    app_label = "execution"
    model_name = "result"


    def test_changelist(self):
        """Result changelist page loads without error, contains name."""
        self.F.ResultFactory.create(tester__username="sometester")

        self.get(self.changelist_url).mustcontain("sometester")


    def test_change_page(self):
        """Result change page loads without error, contains name."""
        r = self.F.ResultFactory.create(tester__username="sometester")

        self.get(self.change_url(r)).mustcontain("sometester")


    def test_change_page_stepresult(self):
        """Result change page includes StepResult inline."""
        sr = self.F.StepResultFactory.create(
            status="failed", result__status="started")

        self.get(self.change_url(sr.result)).mustcontain("failed")
