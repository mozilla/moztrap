"""
Tests for RunSuite model.

"""
from tests import case



class RunSuiteTest(case.DBTestCase):
    def test_unicode(self):
        rs = self.F.RunSuiteFactory(run__name="FF10", suite__name="Speed")

        self.assertEqual(unicode(rs), u"Suite 'Speed' included in run 'FF10'")
