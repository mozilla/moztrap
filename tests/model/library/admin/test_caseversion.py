"""
Tests for CaseVersion admin.

"""
from mock import patch

from tests import case



class CaseVersionAdminTest(case.admin.AdminTestCase):
    app_label = "library"
    model_name = "caseversion"


    def test_changelist(self):
        """CaseVersion changelist page loads without error, contains name."""
        self.F.CaseVersionFactory.create(name="Can load a website")

        self.get(self.changelist_url).mustcontain("Can load a website")


    def test_change_page(self):
        """CaseVersion change page loads without error, contains name."""
        p = self.F.CaseVersionFactory.create(name="Can load a website")

        self.get(self.change_url(p)).mustcontain("Can load a website")


    def test_change_page_step(self):
        """CaseVersion change page includes CaseStep inline."""
        s = self.F.CaseStepFactory.create(instruction="Type a URL in the address bar")

        self.get(self.change_url(s.caseversion)).mustcontain(
            "Type a URL in the address bar")


    def test_change_page_attachment(self):
        """CaseVersion change page includes CaseAttachment inline."""
        a = self.F.CaseAttachmentFactory.create(name="FooBar")

        self.get(self.change_url(a.caseversion)).mustcontain("FooBar")


    def test_change_page_tag(self):
        """CaseVersion change page includes CaseTag inline."""
        t = self.F.TagFactory.create(name="some tag")
        c = self.F.CaseVersionFactory.create()
        c.tags.add(t)

        self.get(self.change_url(c)).mustcontain("some tag")


    def get_envs(self):
        """Returns an Environment."""
        return self.F.EnvironmentFactory.create_set(["OS"], ["Linux"])


    def test_add_step_with_caseversion(self):
        """Can add inline step along with new caseversion."""
        envs = self.get_envs()
        pv = self.F.ProductVersionFactory.create()
        case = self.F.CaseFactory.create(product=pv.product)

        # patching extra avoids need for JS to add step
        with patch("moztrap.model.library.admin.CaseStepInline.extra", 1):
            form = self.get(self.add_url).forms[0]
            form["case"] = str(case.id)
            form["productversion"] = str(pv.id)
            form["name"] = "Some case"
            form["steps-0-number"] = "1"
            form["steps-0-instruction"] = "An instruction"
            form["steps-0-expected"] = "A result"
            res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(
            case.versions.get().steps.get().instruction, "An instruction")


    def test_add_step_tracks_user(self):
        """Adding a CaseStep via inline tracks created-by user."""
        cv = self.F.CaseVersionFactory.create()
        cv.environments.add(*self.get_envs())

        # patching extra avoids need for JS to submit new step
        with patch("moztrap.model.library.admin.CaseStepInline.extra", 1):
            form = self.get(self.change_url(cv)).forms[0]
            form["steps-0-number"] = "1"
            form["steps-0-instruction"] = "An instruction"
            form["steps-0-expected"] = "A result"
            res = form.submit()
        self.assertEqual(res.status_int, 302)

        s = cv.steps.get()

        self.assertEqual(s.created_by, self.user)


    def test_change_step_tracks_user(self):
        """Modifying a CaseStep via inline tracks modified-by user."""
        s = self.F.CaseStepFactory.create(
            instruction="Type a URL in the address bar")
        s.caseversion.environments.add(*self.get_envs())

        form = self.get(self.change_url(s.caseversion)).forms[0]
        form["steps-0-instruction"] = "A new instruction"
        res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(self.refresh(s).modified_by, self.user)


    def test_delete_step_tracks_user(self):
        """Deleting a CaseStep via inline tracks modified-by user."""
        s = self.F.CaseStepFactory.create()
        s.caseversion.environments.add(*self.get_envs())

        form = self.get(self.change_url(s.caseversion)).forms[0]
        form["steps-0-DELETE"] = True
        res = form.submit()
        self.assertEqual(res.status_int, 302)

        self.assertEqual(self.refresh(s).deleted_by, self.user)


    def test_remove_env_narrowing(self):
        """Remove env narrowing via bulk-action."""
        envs = self.F.EnvironmentFactory.create_full_set({"OS": ["OS X", "Linux"]})
        pv = self.F.ProductVersionFactory.create(environments=envs[1:])
        cv1 = self.F.CaseVersionFactory.create(productversion=pv, envs_narrowed=True)

        pv.add_envs(envs[0])

        form = self.get(self.changelist_url).forms["changelist-form"]
        form["action"] = "remove_env_narrowing"
        form["_selected_action"] = str(cv1.id)
        form.submit("index", 0)

        self.assertEqual(set(cv1.environments.all()), set(envs))

