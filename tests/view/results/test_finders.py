"""
Tests for results finder.

"""
from django.core.urlresolvers import reverse

from tests import case



class CaseColumnTest(case.DBTestCase):
    """Tests for results finder CaseColumn."""
    @property
    def column(self):
        """The Column class under test."""
        from moztrap.view.results.finders import CaseColumn
        return CaseColumn


    def test_goto_url(self):
        """goto_url returns results list url for given RCV."""
        c = self.column(
            None,
            None,
            self.model.RunCaseVersion.objects.all(),
            "results_results",
            )
        rcv = self.F.RunCaseVersionFactory.create()

        url = c.goto_url(rcv)

        self.assertEqual(
            url, reverse("results_results", kwargs={"rcv_id": rcv.id}))


    def test_no_goto_url(self):
        """goto_url still returns None if no url name given."""
        c = self.column(
            None,
            None,
            self.model.RunCaseVersion.objects.all(),
            )
        rcv = self.F.RunCaseVersionFactory.create()

        self.assertIsNone(c.goto_url(rcv))
