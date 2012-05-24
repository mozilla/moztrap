"""
Tests for test case queryset-filtering by ID and with optional ID prefix.

"""
from sets import Set
from tests import case
from moztrap.view.lists.cases import PrefixIDFilter



class PrefixIDFilterTest(case.DBTestCase):
    """Tests for PrefixIDFilter"""

    def create_testdata(self):
        testdata = {}

        testdata["cv1"] = self.F.CaseVersionFactory.create(name="CV 1",
            case=self.F.CaseFactory.create(idprefix="pre"))
        testdata["cv2"] = self.F.CaseVersionFactory.create(name="CV 2")
        testdata["cv3"] = self.F.CaseVersionFactory.create(name="CV 3",
            case=self.F.CaseFactory.create(idprefix="moz"))
        testdata["cv4"] = self.F.CaseVersionFactory.create(name="CV 4",
            case=self.F.CaseFactory.create(idprefix="moz"))

        return testdata


    def filter(self, criteria):
        f = PrefixIDFilter("id")
        res = f.filter(
            self.model.CaseVersion.objects.all(),
            criteria,
            )
        return res


    def test_prefix_and_id(self):
        """prefix and ID"""
        td = self.create_testdata()
        res = self.filter([u"pre-{0}".format(td["cv1"].case.id)])

        self.assertEqual(res.get().name, "CV 1")


    def test_prefix_only(self):
        """prefix only"""
        self.create_testdata()
        res = self.filter([u"pre"])

        self.assertEqual(res.get().name, "CV 1")


    def test_id_only(self):
        """ID only"""
        td = self.create_testdata()
        res = self.filter([unicode(td["cv1"].case.id)])

        self.assertEqual(res.get().name, "CV 1")


    def test_id_and_prefix_from_different_cases_gets_both(self):
        """ID from one case and prefix from a different case gets both"""
        td = self.create_testdata()
        res = self.filter([u"pre", unicode(td["cv2"].case.id)])

        self.assertEqual(
            Set([x.name for x in res.all()]),
            Set(["CV 1", "CV 2"]),
            )


    def test_id_case_without_prefix(self):
        """id when case has no prefix"""
        td = self.create_testdata()
        res = self.filter([unicode(td["cv2"].case.id)])

        self.assertEqual(res.get().name, "CV 2")


    def test_cases_different_prefix_return_both(self):
        """
        3 cases have 2 different prefixes returns cases from both prefixes.
        """
        self.create_testdata()
        res = self.filter([u"pre", u"moz"])

        self.assertEqual(
            Set([x.name for x in res.all()]),
            Set(["CV 1", "CV 3", "CV 4"]),
            )


    def test_cases_same_prefix_return_both(self):
        """2 cases with no prefixes, IDs OR'ed"""
        self.create_testdata()
        res = self.filter([u"moz"])

        self.assertEqual(
            Set([x.name for x in res.all()]),
            Set(["CV 3", "CV 4"]),
            )
