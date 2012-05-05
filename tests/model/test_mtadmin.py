"""
Tests for MT base admin forms.

"""
from django.core.urlresolvers import reverse

from django.contrib.admin.sites import AdminSite

from tests import case



class MTAdminSiteTest(case.view.ViewTestCase):
    """Tests of MTAdminSite"""
    @property
    def url(self):
        return reverse("admin:index")


    def test_login_redirect(self):
        """No-user redirects to front-end login page with ?next parameter."""
        res = self.get()

        self.assertRedirects(res, "/users/login/?next=/admin/")


    def test_login_redirect_message(self):
        """Non-admin user redirects to login with message."""
        res = self.get(user=self.F.UserFactory.create())

        self.assertRedirects(res, "/users/login/?next=/admin/")
        res.follow().mustcontain("have permission")



class TeamModelAdminTest(case.DBTestCase):
    """Tests of TeamModelAdmin."""
    @property
    def admin(self):
        """The model admin class under test."""
        from moztrap.model.mtadmin import TeamModelAdmin
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
