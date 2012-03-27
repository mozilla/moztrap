"""
Tests for RunCaseVersion admin.

"""
from tests import case



class RunCaseVersionAdminTest(case.admin.AdminTestCase):
    app_label = "execution"
    model_name = "runcaseversion"


    def test_changelist(self):
        """RunCaseVersion changelist page loads without error, contains name."""
        self.F.RunCaseVersionFactory.create(run__name="Some Run")

        self.get(self.changelist_url).mustcontain("Some Run")


    def test_change_page(self):
        """RunCaseVersion change page loads without error, contains name."""
        rcv = self.F.RunCaseVersionFactory.create(run__name="Some Run")

        self.get(self.change_url(rcv)).mustcontain("Some Run")


    def test_change_page_suite(self):
        """RunCaseVersion change page includes Result inline."""
        r = self.F.ResultFactory.create(tester__username="sometester")

        self.get(self.change_url(r.runcaseversion)).mustcontain("sometester")
