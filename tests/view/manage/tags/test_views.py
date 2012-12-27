# coding: utf-8
"""
Tests for tag management views.

"""
from django.core.urlresolvers import reverse

from tests import case



class TagsTest(case.view.manage.ListViewTestCase,
               case.view.manage.MTModelListTests,
               case.view.NoCacheTest,
               ):
    """Test for tags manage list view."""
    form_id = "manage-tags-form"
    perm = "manage_tags"


    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.TagFactory


    @property
    def url(self):
        """Shortcut for manage-tags url."""
        return reverse("manage_tags")


    def test_filter_by_name(self):
        """Can filter by name."""
        self.factory.create(name="Tag 1")
        self.factory.create(name="Tag 2")

        res = self.get(params={"filter-name": "1"})

        self.assertInList(res, "Tag 1")
        self.assertNotInList(res, "Tag 2")


    def test_sort_by_name(self):
        """Can sort by name."""
        self.factory.create(name="Tag 1")
        self.factory.create(name="Tag 2")

        res = self.get(params={"sortfield": "name", "sortdirection": "desc"})

        self.assertOrderInList(res, "Tag 2", "Tag 1")


    def test_filter_by_product(self):
        """Can filter by product."""
        p = self.F.ProductFactory.create()
        self.factory.create(name="Tag 1", product=p)
        self.factory.create(name="Tag 2")

        res = self.get(params={"filter-product": str(p.id)})

        self.assertInList(res, "Tag 1")
        self.assertNotInList(res, "Tag 2")


    def test_filter_by_productversion(self):
        """Can filter by product of productversion."""
        pv1 = self.F.ProductVersionFactory()
        pv2 = self.F.ProductVersionFactory()
        one = self.factory.create(name="Foo 1", product=pv1.product)
        self.factory.create(name="Foo 2", product=pv2.product)

        res = self.get(
            params={"filter-productversion": str(pv1.id)})

        self.assertInList(res, "Foo 1")
        self.assertNotInList(res, "Foo 2")


    def test_sort_by_product(self):
        """Can sort by product."""
        pb = self.F.ProductFactory.create(name="B")
        pa = self.F.ProductFactory.create(name="A")
        self.factory.create(name="Tag 1", product=pb)
        self.factory.create(name="Tag 2", product=pa)

        res = self.get(params={"sortfield": "product", "sortdirection": "asc"})

        self.assertOrderInList(res, "Tag 2", "Tag 1")



class TagDetailTest(case.view.AuthenticatedViewTestCase,
                      case.view.NoCacheTest,
                      ):
    """Test for tag-detail ajax view."""
    def setUp(self):
        """Setup for case details tests; create a suite."""
        super(TagDetailTest, self).setUp()
        self.tag = self.F.TagFactory.create()


    @property
    def url(self):
        """Shortcut for suite detail url."""
        return reverse(
            "manage_tag_details",
            kwargs=dict(tag_id=self.tag.id)
        )


    def test_details_description(self):
        """Details includes description, markdownified safely."""
        self.tag.description = "_foodesc_ <script>"
        self.tag.save()

        res = self.get(headers={"X-Requested-With": "XMLHttpRequest"})

        res.mustcontain("<em>foodesc</em> &lt;script&gt;")



class AddTagTest(case.view.FormViewTestCase,
                 case.view.NoCacheTest,
                 ):
    """Tests for add tag view."""
    form_id = "tag-add-form"


    @property
    def url(self):
        """Shortcut for add-tag url."""
        return reverse("manage_tag_add")


    def setUp(self):
        """Add manage-tags permission to user."""
        super(AddTagTest, self).setUp()
        self.add_perm("manage_tags")


    def test_success(self):
        """Can add a tag with basic data, including a product."""
        p = self.F.ProductFactory.create()
        form = self.get_form()
        form["name"] = "Some browser ùê"
        form["product"] = str(p.id)

        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_tags"))

        res.follow().mustcontain("Tag 'Some browser ùê' added.")

        t = self.model.Tag.objects.get()
        self.assertEqual(unicode(t.name), u"Some browser ùê")
        self.assertEqual(t.product, p)


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_manage_tags_permission(self):
        """Requires manage-tags permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")



class EditTagTest(case.view.FormViewTestCase,
                  case.view.NoCacheTest,
                  ):
    """Tests for edit-tag view."""
    form_id = "tag-edit-form"


    def setUp(self):
        """Setup for tag edit tests; create a tag, add perm."""
        super(EditTagTest, self).setUp()
        self.tag = self.F.TagFactory.create()
        self.add_perm("manage_tags")


    @property
    def url(self):
        """Shortcut for edit-tag url."""
        return reverse(
            "manage_tag_edit", kwargs=dict(tag_id=self.tag.id))


    def test_requires_manage_tags_permission(self):
        """Requires manage-tags permission."""
        res = self.app.get(self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")


    def test_save_basic(self):
        """Can save updates; redirects to manage tags list."""
        p = self.F.ProductFactory.create()
        form = self.get_form()
        form["name"] = "new name ùê"
        form["product"] = str(p.id)
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_tags"))

        res.follow().mustcontain("Saved 'new name ùê'.")

        t = self.refresh(self.tag)
        self.assertEqual(unicode(t.name), u"new name ùê")
        self.assertEqual(t.product, p)


    def test_errors(self):
        """Test bound form redisplay with errors."""
        form = self.get_form()
        form["name"] = ""
        res = form.submit(status=200)

        res.mustcontain("This field is required.")


    def test_concurrency_error(self):
        """Concurrency error is displayed."""
        form = self.get_form()

        self.tag.save()

        form["name"] = "New"
        res = form.submit(status=200)

        res.mustcontain("Another user saved changes to this object")



class TagsAutocompleteTest(case.view.AuthenticatedViewTestCase,
                           case.view.NoCacheTest,
                           ):
    """Test for tags autocomplete view."""
    @property
    def url(self):
        """Shortcut for tag-autocomplete url."""
        return reverse("manage_tags_autocomplete")


    def get(self, query=None):
        """Shortcut for getting tag-autocomplete url authenticated."""
        url = self.url
        if query is not None:
            url = url + "?text=" + query
        return self.app.get(url, user=self.user)


    def test_matching_tags_json(self):
        """Returns list of matching tags in JSON."""
        t = self.F.TagFactory.create(name="foùêo")

        res = self.get("o")

        self.assertEqual(
            res.json,
            {
                "suggestions": [
                    {
                        "id": t.id,
                        "name": u"foùêo",
                        "postText": u"ùêo",
                        "preText": "f",
                        "product-id": None,
                        "type": "tag",
                        "typedText": "o",
                        }
                    ]
                }
            )


    def test_not_wrong_product_tags(self):
        """Only tags for the correct product, or global tags, are returned."""
        p1 = self.F.ProductFactory.create()
        p2 = self.F.ProductFactory.create()

        t1 = self.F.TagFactory.create(product=p1, name="t1")
        self.F.TagFactory.create(product=p2, name="t2")
        t3 = self.F.TagFactory.create(product=None, name="t3")

        res = self.app.get(
            self.url, user=self.user, params={"text": "t", "product-id": p1.id})

        self.assertEqual(
            [(t["id"], t["product-id"]) for t in res.json["suggestions"]],
            [(t1.id, p1.id), (t3.id, None)]
            )


    def test_case_insensitive(self):
        """Matching is case-insensitive, but pre/post are case-accurate."""
        t = self.F.TagFactory.create(name="FooBar")

        res = self.get("oO")

        self.assertEqual(
            res.json,
            {
                "suggestions": [
                    {
                        "id": t.id,
                        "name": "FooBar",
                        "postText": "Bar",
                        "preText": "F",
                        "product-id": None,
                        "type": "tag",
                        "typedText": "oO",
                        }
                    ]
                }
            )


    def test_no_query(self):
        """If no query is provided, no tags are returned."""
        self.F.TagFactory.create(name="foo")

        res = self.get()

        self.assertEqual(res.json, {"suggestions": []})
