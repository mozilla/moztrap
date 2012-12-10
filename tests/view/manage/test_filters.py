"""
Tests for filtering.

"""
from mock import Mock

from django.utils.datastructures import MultiValueDict

from tests import case



class CaseVersionFilterSetTest(case.DBTestCase):
    """Tests for CaseVersionFilterSet."""
    def bound(self, GET):
        """Return instance of bound filter set."""
        from moztrap.view.filters import CaseVersionFilterSet
        return CaseVersionFilterSet().bind(GET)


    def test_filtered_by_productversion(self):
        """If filtered by productversion, doesn't filter by latest=True."""
        pv = self.F.ProductVersionFactory.create()

        fs = self.bound(MultiValueDict({"filter-productversion": [str(pv.id)]}))

        qs = Mock()
        qs2 = fs.filter(qs)

        qs.filter.assert_called_with(productversion__in=[pv.id])
        # no other filters intervening
        self.assertIs(qs2, qs.filter.return_value.distinct.return_value)
