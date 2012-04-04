"""
Tests for case management views.

"""
from django.conf import settings
from django.core.urlresolvers import reverse

from tests import case



class CasesTest(case.view.manage.ListViewTestCase,
                case.view.ListFinderTests,
                case.view.manage.MTModelListTests,
                case.view.manage.StatusListTests,
                case.view.NoCacheTest,
                ):
    """Test for cases manage list view."""
    form_id = "manage-cases-form"
    perm = "manage_cases"


    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.CaseVersionFactory


    @property
    def url(self):
        """Shortcut for manage-cases url."""
        return reverse("manage_cases")


    def test_create_link(self):
        """With proper perm, create links are there."""
        self.add_perm("create_cases")
        res = self.get()

        self.assertElement(res.html, "a", "create", count=2)


    def test_lists_latest_versions(self):
        """Lists only latest version of each case."""
        cv = self.F.CaseVersionFactory.create(
            name="Old Version", productversion__version="1.0")
        self.F.CaseVersionFactory.create(
            name="Latest Version",
            case=cv.case,
            productversion__product=cv.productversion.product,
            productversion__version="2.0")

        res = self.get()

        self.assertNotInList(res, "Old Version")
        self.assertInList(res, "Latest Version")


    def test_filter_by_status(self):
        """Can filter by status."""
        self.F.CaseVersionFactory.create(status="draft", name="Case 1")
        self.F.CaseVersionFactory.create(status="active", name="Case 2")

        res = self.get(params={"filter-status": "draft"})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_id(self):
        """Can filter by id."""
        cv1 = self.F.CaseVersionFactory.create(name="Case 1")
        self.F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"filter-id": cv1.case.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_bad_id(self):
        """Attempt to filter by non-integer id returns no items."""
        self.F.CaseVersionFactory.create(name="Case 1")

        res = self.get(params={"filter-id": "foo"})

        self.assertNotInList(res, "Case 1")


    def test_filter_by_name(self):
        """Can filter by name."""
        self.F.CaseVersionFactory.create(name="Case 1")
        self.F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"filter-name": "1"})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_tag(self):
        """Can filter by tag."""
        t = self.F.TagFactory.create()
        cv = self.F.CaseVersionFactory.create(name="Case 1")
        cv.tags.add(t)
        self.F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"filter-tag": t.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_product(self):
        """Can filter by product."""
        cv = self.F.CaseVersionFactory.create(name="Case 1")
        self.F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"filter-product": cv.case.product.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_productversion(self):
        """Can filter by product version; no implicit filter by latest."""
        cv = self.F.CaseVersionFactory.create(name="Case 1")
        self.F.CaseVersionFactory.create(
            name="Case 2",
            case=cv.case,
            productversion__product=cv.productversion.product,
            productversion__version="2.0")

        res = self.get(params={"filter-productversion": cv.productversion.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_step_instruction(self):
        """Can filter by step instruction."""
        self.F.CaseStepFactory.create(
            caseversion__name="Case 1", instruction="do this")
        self.F.CaseStepFactory.create(
            caseversion__name="Case 2", instruction="do that")

        res = self.get(params={"filter-instruction": "this"})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_step_expected_result(self):
        """Can filter by step expected result."""
        self.F.CaseStepFactory.create(
            caseversion__name="Case 1", expected="see this")
        self.F.CaseStepFactory.create(
            caseversion__name="Case 2", expected="see that")

        res = self.get(params={"filter-expected": "this"})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_env_elements(self):
        """Can filter by environment elements."""
        envs = self.F.EnvironmentFactory.create_full_set(
            {"OS": ["Linux", "Windows"]})
        self.F.CaseVersionFactory.create(name="Case 1", environments=envs)
        self.F.CaseVersionFactory.create(name="Case 2", environments=envs[1:])

        res = self.get(
            params={"filter-envelement": envs[0].elements.all()[0].id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_filter_by_suite(self):
        """Can filter by suite."""
        cv = self.F.CaseVersionFactory.create(name="Case 1")
        self.F.CaseVersionFactory.create(name="Case 2")
        sc = self.F.SuiteCaseFactory.create(case=cv.case)

        res = self.get(params={"filter-suite": sc.suite.id})

        self.assertInList(res, "Case 1")
        self.assertNotInList(res, "Case 2")


    def test_sort_by_status(self):
        """Can sort by status."""
        self.F.CaseVersionFactory.create(name="Case 1", status="draft")
        self.F.CaseVersionFactory.create(name="Case 2", status="active")

        res = self.get(params={"sortfield": "status", "sortdirection": "asc"})

        self.assertOrderInList(res, "Case 2", "Case 1")


    def test_sort_by_name(self):
        """Can sort by name."""
        self.F.CaseVersionFactory.create(name="Case 1")
        self.F.CaseVersionFactory.create(name="Case 2")

        res = self.get(params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Case 2", "Case 1")



class CaseDetailTest(case.view.AuthenticatedViewTestCase,
                     case.view.NoCacheTest,
                     ):
    """Test for case-detail ajax view."""
    def setUp(self):
        """Setup for case details tests; create a caseversion."""
        super(CaseDetailTest, self).setUp()
        self.cv = self.F.CaseVersionFactory.create()


    @property
    def url(self):
        """Shortcut for case-details url."""
        return reverse(
            "manage_case_details", kwargs=dict(caseversion_id=self.cv.id))


    def test_description(self):
        """Details includes description, markdownified safely."""
        self.cv = self.F.CaseVersionFactory.create(
            description="_Valmorphanize_ <script>",
            )
        res = self.get(ajax=True)

        res.mustcontain("<em>Valmorphanize</em> &lt;script&gt;")


    def test_step(self):
        """Details includes steps, markdownified safely."""
        self.F.CaseStepFactory.create(
            caseversion=self.cv,
            instruction="<script>alert(foo);</script>",
            expected="{@onclick=alert(1)}paragraph",
            ).caseversion

        res = self.get(ajax=True)

        res.mustcontain("<p>&lt;script&gt;alert(foo);&lt;/script&gt;</p>")
        res.mustcontain("<p>{@onclick=alert(1)}paragraph</p>")



class CaseTest(case.view.AuthenticatedViewTestCase):
    """Tests for case-id redirect view."""
    def setUp(self):
        """Setup for case-url tests; creates a case."""
        super(CaseTest, self).setUp()
        self.case = self.F.CaseFactory.create()


    @property
    def url(self):
        """Shortcut for case-id redirect view."""
        return reverse("manage_case", kwargs=dict(case_id=self.case.id))


    def test_redirect(self):
        """Redirects to show latest version of this case in manage list."""
        self.F.CaseVersionFactory(
            productversion__version="1.0",
            productversion__product=self.case.product,
            case=self.case,
            )
        cv = self.F.CaseVersionFactory(
            productversion__version="2.0",
            productversion__product=self.case.product,
            case=self.case,
            )

        res = self.get()

        self.assertRedirects(
            res,
            "{0}#caseversion-id-{1}".format(reverse("manage_cases"), cv.id),
            )


    def test_deleted_version(self):
        """Excludes deleted versions from consideration."""
        self.F.CaseVersionFactory(
            productversion__version="1.0",
            productversion__product=self.case.product,
            case=self.case,
            ).delete()
        cv = self.F.CaseVersionFactory(
            productversion__version="2.0",
            productversion__product=self.case.product,
            case=self.case,
            )

        res = self.get()

        self.assertRedirects(
            res,
            "{0}#caseversion-id-{1}".format(reverse("manage_cases"), cv.id),
            )



class AddCaseTest(case.view.FormViewTestCase,
                  case.view.NoCacheTest,
                  ):
    """Tests for add-case-single view."""
    form_id = "single-case-add"


    @property
    def url(self):
        """Shortcut for add-case-single url."""
        return reverse("manage_case_add")


    def setUp(self):
        """Add create-cases permission to user."""
        super(AddCaseTest, self).setUp()
        self.add_perm("create_cases")


    def test_success(self):
        """Can add a test case with basic data, including a step."""
        pv = self.F.ProductVersionFactory.create()

        form = self.get_form()
        form["product"] = pv.product.id
        form["productversion"] = pv.id
        form["name"] = "Can log in."
        form["description"] = "Tests that a user can log in."
        form["steps-0-instruction"] = "Type creds and click login."
        form["steps-0-expected"] = "You should see a welcome message."
        form["status"] = "active"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_cases"))

        res.follow().mustcontain("Test case 'Can log in.' added.")

        from moztrap.model import CaseVersion
        cv = CaseVersion.objects.get()
        self.assertEqual(cv.case.product, pv.product)
        self.assertEqual(cv.productversion, pv)
        self.assertEqual(cv.name, "Can log in.")
        self.assertEqual(cv.description, "Tests that a user can log in.")
        self.assertEqual(cv.status, "active")
        step = cv.steps.get()
        self.assertEqual(step.instruction, "Type creds and click login.")
        self.assertEqual(step.expected, "You should see a welcome message.")


    def test_prepopulate_from_querystring(self):
        """Can prepopulate the form via the GET querystring."""
        self.add_perm("manage_suite_cases")

        s = self.F.SuiteFactory.create()
        form = self.get_form(params={"initial_suite": str(s.id)})

        self.assertEqual(form.fields["initial_suite"][0].value, str(s.id))


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_create_cases_permission(self):
        """Requires create-cases permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")



class AddBulkCaseTest(case.view.FormViewTestCase,
                      case.view.NoCacheTest,
                      ):
    """Tests for add-case-bulk view."""
    form_id = "bulk-case-add"


    @property
    def url(self):
        """Shortcut for add-case-bulk url."""
        return reverse("manage_case_add_bulk")


    def setUp(self):
        """Add create-cases permission to user."""
        super(AddBulkCaseTest, self).setUp()
        self.add_perm("create_cases")


    def test_success(self):
        """Can add a test case or two with basic data, including a step."""
        pv = self.F.ProductVersionFactory.create()

        form = self.get_form()
        form["product"] = pv.product.id
        form["productversion"] = pv.id
        form["cases"] = (
            "Test that I can log in\n"
            "description here\n"
            "When I type creds and click login\n"
            "Then I should see a welcome message.\n"
            "Test that I can register\n"
            "When I register\n"
            "Then I am registered\n"
            )
        form["status"] = "active"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_cases"))

        res.follow().mustcontain("Added 2 test cases.")

        from moztrap.model import CaseVersion
        cv1, cv2 = list(CaseVersion.objects.all())

        self.assertEqual(cv1.case.product, pv.product)
        self.assertEqual(cv1.productversion, pv)
        self.assertEqual(cv1.name, "Test that I can log in")
        self.assertEqual(cv1.description, "description here")
        self.assertEqual(cv1.status, "active")
        step = cv1.steps.get()
        self.assertEqual(step.instruction, "When I type creds and click login")
        self.assertEqual(step.expected, "Then I should see a welcome message.")

        self.assertEqual(cv2.case.product, pv.product)
        self.assertEqual(cv2.productversion, pv)
        self.assertEqual(cv2.name, "Test that I can register")
        self.assertEqual(cv2.description, "")
        self.assertEqual(cv2.status, "active")
        step = cv2.steps.get()
        self.assertEqual(step.instruction, "When I register")
        self.assertEqual(step.expected, "Then I am registered")


    def test_success_single(self):
        """Confirmation message for single add is grammatically correct."""
        pv = self.F.ProductVersionFactory.create()

        form = self.get_form()
        form["product"] = pv.product.id
        form["productversion"] = pv.id
        form["cases"] = (
            "Test that I can log in\n"
            "description here\n"
            "When I type creds and click login\n"
            "Then I should see a welcome message.\n"
            )
        res = form.submit(status=302)

        res.follow().mustcontain("Added 1 test case.")


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_create_cases_permission(self):
        """Requires create-cases permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")



class CloneCaseVersionTest(case.view.AuthenticatedViewTestCase):
    """Tests for caseversion-clone view."""
    csrf_checks = False


    def setUp(self):
        """Setup for caseversion clone tests; create a caseversion, add perm."""
        super(CloneCaseVersionTest, self).setUp()
        self.cv = self.F.CaseVersionFactory.create(
            name="Can log in", productversion__product__name="MozTrap")
        self.add_perm("manage_cases")


    @property
    def url(self):
        """Shortcut for caseversion-clone url."""
        return reverse(
            "manage_caseversion_clone", kwargs=dict(caseversion_id=self.cv.id))


    def test_login_required(self):
        """Requires login."""
        res = self.app.post(
            self.url,
            {"csrfmiddlewaretoken": "foo"},
            headers={"Cookie": "{0}=foo".format(settings.CSRF_COOKIE_NAME)},
            status=302,
            )

        self.assertRedirects(res, reverse("auth_login") + "?next=" + self.url)


    def test_manage_cases_permission_required(self):
        """Requires manage cases permission."""
        res = self.app.post(
            self.url,
            {"csrfmiddlewaretoken": "foo"},
            headers={"Cookie": "{0}=foo".format(settings.CSRF_COOKIE_NAME)},
            user=self.F.UserFactory.create(),
            status=302,
            )

        self.assertRedirects(res, "/")


    def test_requires_post(self):
        """View only accepts POST."""
        self.get(status=405)


    def test_no_productversion_id(self):
        """If no productversion id, redirects back to original caseversion."""
        res = self.post({}, status=302)

        self.assertRedirects(
            res,
            reverse(
                "manage_caseversion_edit",
                kwargs=dict(caseversion_id=self.cv.id)
                )
            )


    def test_bad_productversion_id(self):
        """If bad productversion id, redirects back to original caseversion."""
        res = self.post({"productversion": 75}, status=302)

        self.assertRedirects(
            res,
            reverse(
                "manage_caseversion_edit",
                kwargs=dict(caseversion_id=self.cv.id)
                )
            )


    def test_already_exists(self):
        """If target caseversion already exists, redirect to edit it."""
        target = self.F.CaseVersionFactory.create(
            case=self.cv.case,
            productversion__product=self.cv.productversion.product,
            productversion__version="2.0")

        res = self.post(
            {"productversion": target.productversion.id}, status=302)

        self.assertRedirects(
            res,
            reverse(
                "manage_caseversion_edit",
                kwargs=dict(caseversion_id=target.id)
                )
            )


    def test_clone(self):
        """If target caseversion doesn't exist yet, clone this one to it."""
        pv = self.F.ProductVersionFactory.create(
            product=self.cv.productversion.product, version="2.0")

        res = self.post({"productversion": pv.id}, status=302)

        res.follow().mustcontain(
            "Created new version of 'Can log in' for MozTrap 2.0.")

        new = pv.caseversions.get()
        self.assertEqual(new.name, self.cv.name)
        self.assertEqual(new.case, self.cv.case)
        self.assertRedirects(
            res,
            reverse(
                "manage_caseversion_edit",
                kwargs=dict(caseversion_id=new.id)
                )
            )



class EditCaseVersionTest(case.view.FormViewTestCase,
                          case.view.NoCacheTest,
                          ):
    """Tests for edit-caseversion view."""
    form_id = "single-case-edit"


    def setUp(self):
        """Setup for caseversion edit tests; create a caseversion, add perm."""
        super(EditCaseVersionTest, self).setUp()
        self.cv = self.F.CaseVersionFactory.create()
        self.add_perm("manage_cases")


    @property
    def url(self):
        """Shortcut for edit-caseversion url."""
        return reverse(
            "manage_caseversion_edit", kwargs=dict(caseversion_id=self.cv.id))


    def test_requires_manage_cases_permission(self):
        """Requires manage-cases permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")


    def test_existing_version_links(self):
        """Page has links to edit other existing versions."""
        other_cv = self.F.CaseVersionFactory.create(
            case=self.cv.case,
            productversion__product=self.cv.case.product,
            productversion__version="2.0"
            )

        res = self.get()

        res.mustcontain(
            reverse(
                "manage_caseversion_edit",
                kwargs=dict(caseversion_id=other_cv.id)
                )
            )


    def test_clone_version_buttons(self):
        """Page has buttons for creating new versions."""
        other_pv = self.F.ProductVersionFactory.create(
            product=self.cv.case.product, version="2.0")

        form = self.get().forms["case-version-list-form"]

        self.assertEqual(len(form.fields["productversion"]), 1)
        self.assertEqual(
            form.fields["productversion"][0].value_if_submitted(),
            str(other_pv.id)
            )


    def test_initial_data(self):
        """Form prepopulates with correct initial data."""
        self.cv.name = "Some name"
        self.cv.description = "Some desc"
        self.cv.status = "active"
        self.cv.save(force_update=True)

        form = self.get_form()

        self.assertEqual(form.fields["name"][0].value, "Some name")
        self.assertEqual(form.fields["description"][0].value, "Some desc")
        self.assertEqual(form.fields["status"][0].value, "active")


    def test_existing_tags(self):
        """Form prepopulates with existing tags."""
        tags = [
            self.F.TagFactory.create(name="one"),
            self.F.TagFactory.create(name="two")
            ]
        self.cv.tags.add(*tags)

        form = self.get_form()

        self.assertEqual(
            [f.value for f in form.fields["tag-tag"]],
            [str(t.id) for t in tags]
            )


    def test_existing_attachments(self):
        """Form prepopulates with remove checkboxes for existing attachments."""
        ca = self.F.CaseAttachmentFactory.create(
            caseversion=self.cv, name="sample.csv")
        self.cv.attachments.add(ca)

        form = self.get_form()

        self.assertEqual(form.fields["remove-attachment"][0].value, None)


    def test_save_basic(self):
        """Can save updates; redirects to manage cases list."""
        form = self.get_form()
        form["status"] = "active"
        form["name"] = "new name"
        form["description"] = "new desc"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_cases"))

        res.follow().mustcontain("Saved 'new name'.")

        cv = self.refresh(self.cv)
        self.assertEqual(cv.name, "new name")
        self.assertEqual(cv.description, "new desc")
        self.assertEqual(cv.status, "active")


    def test_edit_step(self):
        """Can edit a step."""
        step = self.F.CaseStepFactory(
            caseversion=self.cv, instruction="do this", expected="see that")

        form = self.get_form()
        form["steps-0-instruction"] = "do something else"
        form["steps-0-expected"] = ""
        form.submit(status=302)

        step = self.refresh(step)
        self.assertEqual(step.instruction, "do something else")
        self.assertEqual(step.expected, "")
        self.assertEqual(step.modified_by, self.user)


    def test_remove_tags(self):
        """Can remove tags."""
        tags = [
            self.F.TagFactory.create(name="one"),
            self.F.TagFactory.create(name="two")
            ]
        self.cv.tags.add(*tags)

        form = self.get_form()
        form.set("tag-tag", None, index=1)
        form.submit(status=302)

        self.assertEqual(list(self.cv.tags.all()), tags[:1])


    def test_remove_attachments(self):
        """Can remove attachments."""
        ca = self.F.CaseAttachmentFactory.create(
            caseversion=self.cv, name="sample.csv")
        self.cv.attachments.add(ca)

        form = self.get_form()
        form["remove-attachment"] = ca.id
        form.submit(status=302)

        self.assertEqual(list(self.cv.attachments.all()), [])


    def test_errors(self):
        """Test bound form redisplay with errors."""
        form = self.get_form()
        form["name"] = ""
        res = form.submit(status=200)

        res.mustcontain("This field is required.")


    def test_concurrency_error(self):
        """Concurrency error is displayed."""
        form = self.get_form()

        self.cv.save()

        form["name"] = "New"
        res = form.submit(status=200)

        res.mustcontain("Another user saved changes to this object")
