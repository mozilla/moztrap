"""
Tests for queryset-filtering.

"""

from tests import case
from moztrap.model.library.models import CaseVersion
from moztrap.view.lists.cases import PrefixIDFilter



class PrefixIDFilterTest(case.DBTestCase):
    """Tests for PrefixIDFilter"""

    @property
    def AllCaseVersions(self):
        return self.model.CaseVersion.objects.all

    def create_testdata(self):
        testdata = {}

        testdata["cv1"] = self.F.CaseVersionFactory.create(
            name="CV 1",
            case=self.F.CaseFactory.create(idprefix="pre"),
            )
        testdata["cv2"] = self.F.CaseVersionFactory.create(name="CV 2")
        testdata["cv3"] = self.F.CaseVersionFactory.create(
            name="CV 3",
            case=self.F.CaseFactory.create(idprefix="moz"),
            )
        testdata["cv4"] = self.F.CaseVersionFactory.create(
            name="CV 4",
            case=self.F.CaseFactory.create(idprefix="moz"),
            )

        return testdata

    def test_prefix_and_id(self):
        """prefix and ID"""
        td = self.create_testdata()
        f = PrefixIDFilter("id")
        res = f.filter(
            self.model.CaseVersion.objects.all(),
            [u"pre-{0}".format(td["cv1"].id)],
            )

        self.assertEqual(res.get().name, "CV 1")


    def test_prefix_only(self):
        """prefix only"""
        self.create_testdata()
        f = PrefixIDFilter("id")
        res = f.filter(self.model.CaseVersion.objects.all(), [u"pre"])

        self.assertEqual(res.get().name, "CV 1")


    def test_id_only(self):
        """ID only"""
        td = self.create_testdata()
        f = PrefixIDFilter("id")
        res = f.filter(
            self.model.CaseVersion.objects.all(),
            [unicode(td["cv1"].id)],
            )

        self.assertEqual(res.get().name, "CV 1")


    def test_id_from_cv1_prefix_from_cv2(self):
        """ID from cv 1, prefix from cv2 gets both"""
        td = self.create_testdata()
        f = PrefixIDFilter("id")
        res = f.filter(
            self.model.CaseVersion.objects.all(),
            [u"pre", unicode(td["cv2"].id)],
            )

        self.assertEqual([x.name for x in res.all()], ["CV 1", "CV 2"])


    def test_id_case_without_prefix(self):
        """id when case has no prefix"""
        td = self.create_testdata()
        f = PrefixIDFilter("id")
        res = f.filter(
            self.model.CaseVersion.objects.all(),
            [unicode(td["cv2"].id)],
            )

        self.assertEqual(res.get().name, "CV 2")


    def test_cases_different_prefix_return_both(self):
        """3 cases have 2 different prefixes OR'ed"""
        self.create_testdata()
        f = PrefixIDFilter("id")
        res = f.filter(
            self.model.CaseVersion.objects.all(),
            [u"pre", u"moz"],
            )

        self.assertEqual([x.name for x in res.all()], ["CV 1", "CV 3", "CV 4"])


    def test_cases_same_prefix_return_both(self):
        """2 cases with no prefixes, IDs OR'ed"""
        self.create_testdata()
        f = PrefixIDFilter("id")
        res = f.filter(
            self.model.CaseVersion.objects.all(),
            [u"moz"],
            )

        self.assertEqual([x.name for x in res.all()], ["CV 3", "CV 4"])
