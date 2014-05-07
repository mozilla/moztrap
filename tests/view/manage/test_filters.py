"""
Tests for filtering.

"""
from mock import Mock

from django.utils.datastructures import MultiValueDict
from django.db.models import Q

from tests import case



class CaseVersionFilterSetTest(case.DBTestCase):
    """Tests for CaseVersionFilterSet."""
    def setUp(self):
        def __str__(self):
            return '{0}{{{1}}}'.format(self.connector, ','.join([str(c) for c in self.children]))

        Q.__str__ = __str__


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

        flt = Q() | Q(**{"productversion__in": [int(pv.id)]})

        flt2 = qs.filter.call_args[0][0]

        self.assertEqual(str(flt), str(flt2))

        # no other filters intervening
        self.assertIs(qs2, qs.filter.return_value.filter.return_value.distinct.return_value)
