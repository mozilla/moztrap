"""
Tests for MozTrap permissions template tags and filters.

"""
from tests import case



class PermissionFilterTest(case.DBTestCase):
    """Tests for permission-related filters."""
    @property
    def permissions(self):
        """The templatetags module under test."""
        from cc.view.templatetags import permissions
        return permissions


    def test_has_perm(self):
        """``has_perm`` filter passes through to user's has_perm method."""
        u = self.F.UserFactory.create(permissions=["library.create_cases"])
        self.assertTrue(self.permissions.has_perm(u, "library.create_cases"))
