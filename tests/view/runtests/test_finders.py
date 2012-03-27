"""
Tests for runtests finder.

"""
from tests import case



class RunTestsFinderTest(case.DBTestCase):
    """Tests for RunTestsFinder."""
    @property
    def finder(self):
        """The Finder class under test."""
        from cc.view.runtests.finders import RunTestsFinder
        return RunTestsFinder


    def test_child_query_url(self):
        """child_query_url returns environments URL for a run, not None."""
        f = self.finder()
        r = self.F.RunFactory.create()

        url = f.child_query_url(r)

        self.assertEqual(
            url, "/runtests/environment/{0}/".format(r.id))


    def test_child_query_url_non_run(self):
        """Given anything but a run, child_query_url defers to Finder."""
        f = self.finder()
        r = self.F.RunFactory.create()

        url = f.child_query_url(r.productversion)

        self.assertEqual(
            url, "?finder=1&col=runs&id={0}".format(r.productversion.id))
