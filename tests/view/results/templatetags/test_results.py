"""
Tests for MozTrap results-views template tags and filters.

"""
from tests import case



class PercentageFilterTest(case.TestCase):
    """Tests for percentage filter."""
    @property
    def filter(self):
        """The template filter under test."""
        from cc.view.results.templatetags.results import percentage
        return percentage


    def test_zero(self):
        """Zero returns zero."""
        self.assertEqual(self.filter(0.0), 0)


    def test_one(self):
        """One returns 100."""
        self.assertEqual(self.filter(1.0), 100)


    def test_near_one(self):
        """Very near one returns 99, not 100."""
        self.assertEqual(self.filter(0.999), 99)


    def test_near_zero(self):
        """Very near zero returns 1, not 0."""
        self.assertEqual(self.filter(0.001), 1)


    def test_round_up(self):
        """Below 0.5, rounds up."""
        self.assertEqual(self.filter(0.45123), 46)


    def test_round_down(self):
        """Above 0.5, rounds down."""
        self.assertEqual(self.filter(0.55987), 55)
