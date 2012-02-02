# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for runtests views.

"""
from django.core.urlresolvers import reverse

from mock import patch

from ... import factories as F

from .. import base



class SelectTest(base.AuthenticatedViewTestCase):
    """Tests for select-run view."""
    @property
    def url(self):
        """Shortcut for runtests url."""
        return reverse("runtests")


    def test_requires_execute_permission(self):
        """Requires execute permission."""
        res = self.app.get(self.url, user=F.UserFactory.create(), status=302)

        self.assertIn("login", res.headers["Location"])


    def test_finder(self):
        """Finder is present in context with list of products."""
        self.add_perm("execute")

        p = F.ProductFactory.create(name="Foo Product")

        res = self.get()

        res.mustcontain("Foo Product")
        res.mustcontain(
            "data-sub-url="
            '"?finder=1&amp;col=productversions&amp;id={0}"'.format(p.id))


    def test_finder_ajax(self):
        """Finder intercepts its ajax requests to return child obj lists."""
        self.add_perm("execute")

        pv = F.ProductVersionFactory.create(version="1.0.1")

        res = self.get(
            params={
                "finder": "1",
                "col": "productversions",
                "id": str(pv.product.id)
                },
            headers={"X-Requested-With": "XMLHttpRequest"},
            )

        self.assertIn("1.0.1", res.json["html"])
        self.assertIn(
            'data-sub-url="?finder=1&amp;col=runs&amp;id={0}"'.format(pv.id),
            res.json["html"]
            )



class SetEnvironmentTest(base.AuthenticatedViewTestCase):
    """Tests for set_environment view."""
    @property
    def url(self):
        """Shortcut for set_environment url."""
        return reverse(
            "runtests_environment", kwargs={"run_id": self.testrun.id})


    @property
    def testrun(self):
        """A lazily-created test run."""
        if getattr(self, "_cached_run", None) is None:
            self._cached_run = F.RunFactory.create(name="Foo Run")
        return self._cached_run


    @property
    def envs(self):
        """A lazily-created sample set of environments."""
        if getattr(self, "_cached_envs", None) is None:
            self._cached_envs = F.EnvironmentFactory.create_full_set(
                {"OS": ["Windows 7", "Ubuntu Linux"]})
        return self._cached_envs


    @property
    def model(self):
        """The models."""
        from cc import model
        return model


    def test_requires_execute_permission(self):
        """Requires execute permission."""
        res = self.app.get(self.url, user=F.UserFactory.create(), status=302)

        self.assertIn("login", res.headers["Location"])


    def test_form_choices(self):
        """Form has available categories and elements for run as choices."""
        self.add_perm("execute")
        self.testrun.environments.add(*self.envs)

        res = self.get()

        res.mustcontain("OS")
        res.mustcontain("Ubuntu Linux")
        res.mustcontain("Windows 7")


    def test_form_initial(self):
        """Form initial choices determined by "environment" session key."""
        self.add_perm("execute")
        self.testrun.environments.add(*self.envs)

        with patch(
                "django.contrib.sessions.backends.cached_db."
                "SessionStore._session_cache",
                {"environment": self.envs[0].id},
                create=True):
            res = self.get()

        res.mustcontain(
            '<option value="{0}" selected="selected">'.format(
                self.envs[0].elements.get().id)
            )


    def test_run(self):
        """Form has test run name in label."""
        self.add_perm("execute")

        res = self.get()

        res.mustcontain("run tests in Foo Run!")


    def test_bad_run_id_404(self):
        """Bad run id returns 404."""
        self.add_perm("execute")
        url = reverse("runtests_environment", kwargs={"run_id": 9999})

        self.app.get(url, user=self.user, status=404)


    def test_ajax(self):
        """Ajax request uses partial template."""
        self.add_perm("execute")

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        self.assertNotIn("<body", res.body)


    def test_env_required(self):
        """Invalid combination results in error."""
        self.add_perm("execute")

        res = self.get().forms["runtests-environment-form"].submit()

        res.mustcontain("selected environment is not valid")


    def test_set_environment(self):
        """Selecting an environment sets it in session."""
        self.add_perm("execute")
        self.testrun.environments.add(*self.envs)

        cat = self.model.Category.objects.get()

        session_data = {}

        with patch(
                "django.contrib.sessions.backends.cached_db."
                "SessionStore._session_cache",
                session_data,
                create=True,
                ):
            form = self.get().forms["runtests-environment-form"]
            form["category_{0}".format(cat.id)] = self.envs[0].elements.get().id

            res = form.submit(status=302)

        self.assertEqual(session_data["environment"], self.envs[0].id)
        self.assertEqual(
            res.headers["Location"],
            "http://localhost:80/runtests/run/{0}/".format(self.testrun.id)
            )
