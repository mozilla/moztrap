"""
Tests for runtests views.

"""
from datetime import datetime

from django.core.urlresolvers import reverse

from BeautifulSoup import BeautifulSoup
from mock import patch

from tests import case



class SelectTest(case.view.AuthenticatedViewTestCase,
                 case.view.NoCacheTest,
                 ):
    """Tests for select-run view."""
    @property
    def url(self):
        """Shortcut for runtests url."""
        return reverse("runtests")


    def test_requires_execute_permission(self):
        """Requires execute permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")


    def test_finder(self):
        """Finder is present in context with list of products."""
        self.add_perm("execute")

        p = self.F.ProductFactory.create(name="Foo Product")

        res = self.get()

        res.mustcontain("Foo Product")
        res.mustcontain(
            "data-sub-url="
            '"?finder=1&amp;col=productversions&amp;id={0}"'.format(p.id))


    def test_finder_ajax(self):
        """Finder intercepts its ajax requests to return child obj lists."""
        self.add_perm("execute")

        pv = self.F.ProductVersionFactory.create(version="1.0.1")

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



class SetEnvironmentTest(case.view.AuthenticatedViewTestCase,
                         case.view.NoCacheTest,
                         ):
    """Tests for set_environment view."""
    def setUp(self):
        """These tests all require a test run."""
        super(SetEnvironmentTest, self).setUp()
        self.testrun = self.F.RunFactory.create(name="Foo Run")


    @property
    def url(self):
        """Shortcut for set_environment url."""
        return reverse(
            "runtests_environment", kwargs={"run_id": self.testrun.id})


    @property
    def envs(self):
        """A lazily-created sample set of environments."""
        if getattr(self, "_cached_envs", None) is None:
            self._cached_envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["Windows 7", "Ubuntu Linux"]})
        return self._cached_envs


    def test_requires_execute_permission(self):
        """Requires execute permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")


    def test_form_choices(self):
        """Form has available categories and elements for run as choices."""
        self.add_perm("execute")
        self.testrun.environments.add(*self.envs)

        res = self.get()

        res.mustcontain("OS")
        res.mustcontain("Ubuntu Linux")
        res.mustcontain("Windows 7")


    def test_valid_environments(self):
        """JSON list of valid envs (as ordered element list) is in template."""
        self.add_perm("execute")
        envs = self.F.EnvironmentFactory.create_set(
            ["OS", "Browser"], ["OS X", "Safari"], ["Windows", "IE"])
        self.testrun.environments.add(*envs)

        osx = self.model.Element.objects.get(name="OS X")
        safari = self.model.Element.objects.get(name="Safari")
        windows = self.model.Element.objects.get(name="Windows")
        ie = self.model.Element.objects.get(name="IE")

        res = self.get()

        res.mustcontain("VALID_ENVIRONMENTS = [")
        res.mustcontain("[{0}, {1}]".format(safari.id, osx.id))
        res.mustcontain("[{0}, {1}]".format(ie.id, windows.id))


    def test_form_initial(self):
        """Form initial choices determined by "environment" querystring key."""
        self.add_perm("execute")
        self.testrun.environments.add(*self.envs)

        res = self.get(params=dict(environment=self.envs[0].id))

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
        """Selecting an environment redirects to run view for that run/env."""
        self.add_perm("execute")
        self.testrun.environments.add(*self.envs)

        cat = self.model.Category.objects.get()

        form = self.get().forms["runtests-environment-form"]
        form["category_{0}".format(cat.id)] = self.envs[0].elements.get().id

        res = form.submit(status=302)

        self.assertRedirects(
            res,
            reverse(
                "runtests_run",
                kwargs={"run_id": self.testrun.id, "env_id": self.envs[0].id})
            )



class RunTestsTest(case.view.AuthenticatedViewTestCase,
                   case.view.NoCacheTest,
                   ):
    """Tests for runtests view."""
    def setUp(self):
        """These tests all require a test run and envs, and execute perm."""
        super(RunTestsTest, self).setUp()
        self.testrun = self.F.RunFactory.create(status="active")
        self.envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Windows 7", "Ubuntu Linux"]})
        self.testrun.environments.add(*self.envs)
        self.add_perm("execute")


    @property
    def url(self):
        """Shortcut for runtests_run url."""
        return reverse(
            "runtests_run",
            kwargs={"run_id": self.testrun.id, "env_id": self.envs[0].id})


    def create_rcv(self, **kwargs):
        """Create a runcaseversion for this run with given kwargs."""
        defaults = {
            "run": self.testrun,
            "caseversion__productversion": self.testrun.productversion,
            "caseversion__case__product": self.testrun.productversion.product,
            "environments": self.envs,
            }
        defaults.update(kwargs)
        return self.F.RunCaseVersionFactory.create(**defaults)


    def create_result(self, **kwargs):
        """Create a result for this run/env/user with given kwargs."""
        defaults = {
            "tester": self.user,
            "environment": self.envs[0]
            }
        defaults.update(kwargs)
        if "runcaseversion" not in defaults:
            defaults["runcaseversion"] = self.create_rcv()
        return self.F.ResultFactory.create(**defaults)


    def test_ajax_get(self):
        """Getting page via ajax returns just itemlist."""
        res = self.get(ajax=True, status=200)

        soup = BeautifulSoup(res.json["html"])

        # outermost element is class "itemlist"
        self.assertIn("itemlist", soup.findChild()["class"])


    def test_requires_execute_permission(self):
        """Requires execute permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")


    def test_markdown_safe(self):
        """Raw HTML and markdown attributes are escaped."""
        rcv = self.create_rcv(caseversion__description="<script>")
        self.F.CaseStepFactory.create(
            caseversion=rcv.caseversion,
            instruction="<script>alert(foo);</script>",
            expected="{@onclick=alert(1)}paragraph",
            )

        res = self.get()

        self.assertEqual(
            unicode(res.html.find("div", "description").find("p")),
            "<p>&lt;script&gt;</p>"
            )

        step = res.html.find("li", {"data-step-number": "1"})
        self.assertEqual(
            unicode(step.find("div", "instruction").find("p")),
            "<p>&lt;script&gt;alert(foo);&lt;/script&gt;</p>"
            )
        self.assertEqual(
            unicode(step.find("div", "outcome").find("p")),
            "<p>{@onclick=alert(1)}paragraph</p>",
            )


    def test_bad_run_id_404(self):
        """Bad run id returns 404."""
        url = reverse("runtests_environment", kwargs={"run_id": 9999})

        self.app.get(url, user=self.user, status=404)


    def test_inactive_run_redirects_to_selector(self):
        """An inactive run redirects to run selector with message."""
        self.testrun.status = "draft"
        self.testrun.save()

        res = self.get(status=302)

        self.assertRedirects(res, reverse("runtests"))
        res.follow().mustcontain("not open for testing")


    def test_invalid_environment_set(self):
        """If env is not valid for run, redirects to set-environment."""
        self.testrun.environments.remove(self.envs[0])

        res = self.get(status=302)

        self.assertRedirects(
            res,
            reverse("runtests_environment", kwargs={"run_id": self.testrun.id})
            )


    def test_environment(self):
        """Environment is shown in template."""
        res = self.get(status=200)

        self.assertEqual(
            res.html.findAll("ul", "envsettings")[0].find("li").text,
            self.envs[0].elements.get().name)


    def test_finder_productversions_prepopulated(self):
        """Finder is prepopulated with product versions."""
        res = self.get(status=200)

        finder_productversions = res.html.findAll(
            "input",
            id="finder-productversions-{0}".format(
                self.testrun.productversion.id)
            )


        self.assertEqual(len(finder_productversions), 1)
        self.assertIn("checked", unicode(finder_productversions[0]))


    def test_finder_runs_prepopulated(self):
        """Finder is prepopulated with runs."""
        res = self.get(status=200)

        finder_runs = res.html.findAll(
            "input", id="finder-runs-{0}".format(self.testrun.id))

        self.assertEqual(len(finder_runs), 1)
        self.assertIn("checked", unicode(finder_runs[0]))


    def test_finder_env_form_prepopulated(self):
        """Finder env form is prepopulated."""
        el = self.envs[0].elements.get()

        res = self.get(status=200)

        form = res.html.find("form", id="runtests-environment-form")
        self.assertEqual(
            form.find("option", value=str(el.id))["selected"], "selected")


    def test_runcaseversions(self):
        """Lists runcaseversions."""
        self.create_rcv(caseversion__name="Foo Case")

        res = self.get(status=200)

        res.mustcontain("Foo Case")


    def test_runcaseversions_env_narrowed(self):
        """Lists only correct env runcaseversions."""
        self.create_rcv(
            caseversion__name="Env0 Case", environments=self.envs[:1])
        self.create_rcv(
            caseversion__name="Env1 Case", environments=self.envs[1:])
        self.create_rcv(caseversion__name="EnvAll Case")

        res = self.get(status=200)

        res.mustcontain("Env0 Case")
        res.mustcontain("EnvAll Case")
        self.assertNotIn("Env1 Case", res)


    def test_redirect_preserves_sort(self):
        """Redirect after non-Ajax post preserves sort params."""
        rcv = self.create_rcv()

        form = self.get(
            params={"sortfield": "name"}, status=200).forms[
            "test-status-form-{0}".format(rcv.id)]

        res = form.submit(name="action-finishsucceed", index=0, status=302)

        self.assertRedirects(res, self.url + "?sortfield=name")


    def test_description(self):
        """Returns details HTML snippet for given caseversion"""

        rcv = self.create_rcv(
            caseversion__name="Foo Case",
            caseversion__description="_Valmorphanize_",
            )

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        res = form.submit(
            name="action-finishsucceed",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"},
            status=200
        )

        res.mustcontain("<em>Valmorphanize</em>")

    def test_post_no_action_redirect(self):
        """POST with no action does nothing and redirects."""
        rcv = self.create_rcv()

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        res = form.submit(status=302)

        self.assertRedirects(res, self.url)


    def test_post_no_action_ajax(self):
        """Ajax POST with no action does nothing and returns no HTML."""
        rcv = self.create_rcv()

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        res = form.submit(
            headers={"X-Requested-With": "XMLHttpRequest"}, status=200)

        self.assertEqual(res.json["html"], "")
        self.assertEqual(res.json["no_replace"], True)


    @patch("moztrap.view.runtests.views.ACTIONS", {})
    def test_post_bad_action_redirect(self):
        """POST with bad action does nothing but message and redirects."""
        rcv = self.create_rcv()

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        # we patched the actions dictionary so "finishsucceed" will not be valid
        res = form.submit(name="action-finishsucceed", index=0, status=302)

        self.assertRedirects(res, self.url)

        res.follow().mustcontain("finishsucceed is not a valid action")


    @patch("moztrap.view.runtests.views.ACTIONS", {})
    def test_post_bad_action_ajax(self):
        """Ajax POST with bad action sets message and returns no HTML."""
        rcv = self.create_rcv()

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        # we patched the actions dictionary so "finishsucceed" will not be valid
        res = form.submit(
            name="action-finishsucceed", index=0,
            headers={"X-Requested-With": "XMLHttpRequest"}, status=200)

        self.assertEqual(res.json["html"], "")
        self.assertEqual(res.json["no_replace"], True)
        self.assertEqual(
            res.json["messages"][0]["message"], "finishsucceed is not a valid action.")


    def test_post_bad_rcv_id_redirect(self):
        """POST with bad rcv id does nothing but message and redirects."""
        rcv = self.create_rcv()

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        rcv.delete()

        res = form.submit(name="action-finishsucceed", index=0, status=302)

        self.assertRedirects(res, self.url)

        res.follow().mustcontain("is not a valid run/caseversion ID")


    def test_post_bad_rcv_id_ajax(self):
        """Ajax POST with bad rcv id sets message and returns no HTML."""
        rcv = self.create_rcv()

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        rcv.delete()

        res = form.submit(
            name="action-finishsucceed", index=0,
            headers={"X-Requested-With": "XMLHttpRequest"}, status=200)

        self.assertEqual(res.json["html"], "")
        self.assertEqual(res.json["no_replace"], True)
        self.assertIn(
            "is not a valid run/caseversion ID",
            res.json["messages"][0]["message"]
            )


    def test_post_missing_result(self):
        """Can pass/fail/invalid a not-yet-existing result."""
        result = self.create_result(status="started")
        rcv = result.runcaseversion

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        result.delete()

        res = form.submit(name="action-finishsucceed", index=0, status=302)

        self.assertRedirects(res, self.url)

        result = rcv.results.get(tester=self.user, environment=self.envs[0])

        self.assertEqual(result.status, result.STATUS.passed)


    def test_post_missing_result_ajax(self):
        """Can pass/fail/invalid a not-yet-existing result via ajax."""
        result = self.create_result(status="started")
        rcv = result.runcaseversion

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        result.delete()

        res = form.submit(
            name="action-finishsucceed", index=0,
            headers={"X-Requested-With": "XMLHttpRequest"}, status=200)

        self.assertElement(
            res.json["html"], "button", attrs={"name": "action-restart"})


    def test_pass_case(self):
        """Submit a "finishsucceed" action for a case; redirects."""
        result = self.create_result(status="started")
        rcv = result.runcaseversion

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        with patch("moztrap.model.execution.models.utcnow") as mock_utcnow:
            mock_utcnow.return_value = datetime(2012, 2, 3)
            res = form.submit(name="action-finishsucceed", index=0, status=302)

        self.assertRedirects(res, self.url)

        result = rcv.results.get(tester=self.user, environment=self.envs[0])

        self.assertEqual(result.status, result.STATUS.passed)
        self.assertEqual(result.completed, datetime(2012, 2, 3))


    def test_pass_case_ajax(self):
        """Ajax post a "finishsucceed" action; returns HTML snippet."""
        result = self.create_result(status="started")
        rcv = result.runcaseversion

        form = self.get(status=200).forms["test-status-form-{0}".format(rcv.id)]

        res = form.submit(
            name="action-finishsucceed",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"},
            status=200
            )

        self.assertElement(
            res.json["html"], "button", attrs={"name": "action-restart"})


    def test_invalidate_case(self):
        """Submit a "finishinvalidate" action for a case; redirects."""
        result = self.create_result(status="started")
        rcv = result.runcaseversion

        form = self.get(status=200).forms[
            "test-invalid-form-{0}".format(rcv.id)]

        form["comment"] = "it ain't valid"

        with patch("moztrap.model.execution.models.utcnow") as mock_utcnow:
            mock_utcnow.return_value = datetime(2012, 2, 3)
            res = form.submit(
                name="action-finishinvalidate", index=0, status=302)

        self.assertRedirects(res, self.url)

        result = rcv.results.get(tester=self.user, environment=self.envs[0])

        self.assertEqual(result.status, result.STATUS.invalidated)
        self.assertEqual(result.comment, "it ain't valid")
        self.assertEqual(result.completed, datetime(2012, 2, 3))


    def test_invalidate_case_ajax(self):
        """Ajax post a "finishinvalidate" action; returns HTML snippet."""
        result = self.create_result(status="started")
        rcv = result.runcaseversion

        form = self.get(status=200).forms[
            "test-invalid-form-{0}".format(rcv.id)]

        form["comment"] = "it ain't valid"

        res = form.submit(
            name="action-finishinvalidate",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"},
            status=200
            )

        self.assertElement(
            res.json["html"], "button", attrs={"name": "action-restart"})


    def test_fail_case(self):
        """Submit a "finishinvalidate" action for a case; redirects."""
        step = self.F.CaseStepFactory.create(number=1)
        rcv = self.create_rcv(caseversion=step.caseversion)
        self.create_result(status="started", runcaseversion=rcv)

        form = self.get(status=200).forms[
            "test-fail-form-{0}-1".format(rcv.id)]

        form["comment"] = "it didn't pass"

        with patch("moztrap.model.execution.models.utcnow") as mock_utcnow:
            mock_utcnow.return_value = datetime(2012, 2, 3)
            res = form.submit(
                name="action-finishfail", index=0, status=302)

        self.assertRedirects(res, self.url)

        result = rcv.results.get(tester=self.user, environment=self.envs[0])

        self.assertEqual(result.status, result.STATUS.failed)
        self.assertEqual(result.comment, "it didn't pass")
        self.assertEqual(result.completed, datetime(2012, 2, 3))


    def test_fail_case_ajax(self):
        """Ajax post a "finishinvalidate" action; returns HTML snippet."""
        step = self.F.CaseStepFactory.create(number=1)
        rcv = self.create_rcv(caseversion=step.caseversion)
        self.create_result(status="started", runcaseversion=rcv)

        form = self.get(status=200).forms[
            "test-fail-form-{0}-1".format(rcv.id)]

        form["comment"] = "it didn't pass"

        res = form.submit(
            name="action-finishfail",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"},
            status=200
            )

        self.assertElement(
            res.json["html"], "button", attrs={"name": "action-restart"})


    def test_restart_case(self):
        """Submit a "restart" action for a case; redirects."""
        result = self.create_result(status="passed")
        rcv = result.runcaseversion

        form = self.get(status=200).forms["restart-form-{0}".format(rcv.id)]

        with patch("moztrap.model.execution.models.utcnow") as mock_utcnow:
            mock_utcnow.return_value = datetime(2012, 2, 3)
            res = form.submit(name="action-restart", index=0, status=302)

        self.assertRedirects(res, self.url)

        result = rcv.results.get(tester=self.user, environment=self.envs[0])

        self.assertEqual(result.status, result.STATUS.started)
        self.assertEqual(result.started, datetime(2012, 2, 3))


    def test_restart_case_ajax(self):
        """Ajax post a "restart" action; returns HTML snippet."""
        result = self.create_result(status="passed")
        rcv = result.runcaseversion

        form = self.get(status=200).forms["restart-form-{0}".format(rcv.id)]

        res = form.submit(
            name="action-restart",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"},
            status=200
            )

        self.assertElement(
            res.json["html"], "button", attrs={"name": "action-finishsucceed"})


    def test_parameter_defaults(self):
        """Action parameters have defaults and are not required."""
        result = self.create_result(status="started")
        rcv = result.runcaseversion

        form = self.get(status=200).forms[
            "test-invalid-form-{0}".format(rcv.id)]

        # prevents any comment parameter from being submitted
        del form.fields["comment"]

        res = form.submit(name="action-finishinvalidate", index=0, status=302)

        self.assertRedirects(res, self.url)

        result = self.refresh(result)

        self.assertEqual(result.status, result.STATUS.invalidated)
        self.assertEqual(result.comment, "")
