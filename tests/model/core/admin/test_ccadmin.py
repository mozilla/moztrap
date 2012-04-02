"""
Tests for CC base admin forms.

"""
from django.contrib.admin.sites import AdminSite

from tests import case



class TeamModelAdminTest(case.DBTestCase):
    """Tests of TeamModelAdmin."""
    @property
    def admin(self):
        """The model admin class under test."""
        from moztrap.model.ccadmin import TeamModelAdmin
        return TeamModelAdmin


    def test_fieldsets(self):
        """Sans declared fieldsets, puts team fields into Team fieldset."""
        ma = self.admin(self.model.ProductVersion, AdminSite())

        fs = ma.get_fieldsets(None, None)

        self.assertEqual(len(fs), 4)

        default, team, deletion, meta = fs

        self.assertNotIn("has_team", default[1]["fields"])
        self.assertNotIn("own_team", default[1]["fields"])
        self.assertEqual(team[0], "Team")
        self.assertEqual(team[1]["fields"], [("has_team", "own_team")])
