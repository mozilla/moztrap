"""
Tests for ProductVersion model.

"""
from datetime import datetime

from django.core.exceptions import ValidationError

from mock import patch

from tests import case



class ProductVersionTest(case.DBTestCase):
    """Tests for ProductVersion model."""
    def test_unicode(self):
        """Unicode representation is product name and version."""
        pv = self.F.ProductVersionFactory(
            product__name="Some Product", version="1.0")

        self.assertEqual(unicode(pv), u"Some Product 1.0")


    def test_name(self):
        """Productversion name is product name and version."""
        pv = self.F.ProductVersionFactory(
            product__name="Some Product", version="1.0")

        self.assertEqual(pv.name, u"Some Product 1.0")


    def test_parent(self):
        """A ProductVersion's ``parent`` property returns its Product."""
        pv = self.F.ProductVersionFactory()

        self.assertIs(pv.parent, pv.product)


    def test_own_team(self):
        """If ``has_team`` is True, ProductVersion's team is its own."""
        pv = self.F.ProductVersionFactory.create(has_team=True)
        u = self.F.UserFactory.create()
        pv.own_team.add(u)

        self.assertEqual(list(pv.team.all()), [u])


    def test_inherit_team(self):
        """If ``has_team`` is False, ProductVersion's team is its parent's."""
        pv = self.F.ProductVersionFactory.create(has_team=False)
        u = self.F.UserFactory.create()
        pv.product.team.add(u)

        self.assertEqual(list(pv.team.all()), [u])


    def test_clone(self):
        """Cloning PV adds ".next" to version, "Cloned:" to codename."""
        c = self.F.ProductVersionFactory.create(
            version="1.0", codename="Foo")

        new = c.clone()

        self.assertNotEqual(new, c)
        self.assertIsInstance(new, type(c))
        self.assertEqual(new.version, "1.0.next")
        self.assertEqual(new.codename, "Cloned: Foo")


    def test_clone_no_runs(self):
        """Cloning a ProductVersion does not clone runs."""
        run = self.F.RunFactory.create()

        new = run.productversion.clone()

        self.assertEqual(len(new.runs.all()), 0)


    def test_clone_no_cases(self):
        """Cloning a ProductVersion does not clone test case versions."""
        cv = self.F.CaseVersionFactory()

        new = cv.productversion.clone()

        self.assertEqual(len(new.caseversions.all()), 0)


    def test_clone_environments(self):
        """Cloning a ProductVersion clones its environments."""
        pv = self.F.ProductVersionFactory(environments={"OS": ["OS X", "Linux"]})

        new = pv.clone()

        self.assertEqual(len(new.environments.all()), 2)


    def test_clone_team(self):
        """Cloning a ProductVersion clones its team."""
        pv = self.F.ProductVersionFactory(team=["One", "Two"])

        new = pv.clone()

        self.assertEqual(len(new.team.all()), 2)


    def test_adding_new_version_reorders(self):
        """Adding a new product version reorders the versions."""
        p = self.F.ProductFactory.create()
        self.F.ProductVersionFactory.create(version="2.11", product=p)
        self.F.ProductVersionFactory.create(version="2.9", product=p)
        self.F.ProductVersionFactory.create(version="2.10", product=p)

        self.assertEqual(
            [(v.version, v.latest) for v in p.versions.all()],
            [("2.9", False), ("2.10", False), ("2.11", True)]
            )


    def test_editing_a_version_reorders(self):
        """Editing a product version reorders the versions."""
        # @@@ what about bulk update of product versions?
        p = self.F.ProductFactory.create()
        self.F.ProductVersionFactory.create(version="2.11", product=p)
        self.F.ProductVersionFactory.create(version="2.9", product=p)
        pv = self.F.ProductVersionFactory.create(version="2.12", product=p)

        pv.version = "2.10"
        pv.save()

        self.assertEqual(
            [(v.version, v.latest) for v in p.versions.all()],
            [("2.9", False), ("2.10", False), ("2.11", True)]
            )


    def test_deleting_a_version_reorders(self):
        """Deleting a product version reorders the versions."""
        # @@@ what about bulk deletion of product versions?
        p = self.F.ProductFactory.create()
        self.F.ProductVersionFactory.create(version="2.10", product=p)
        self.F.ProductVersionFactory.create(version="2.9", product=p)

        self.F.ProductVersionFactory.create(version="2.11", product=p).delete()

        self.assertEqual(
            [(v.version, v.latest) for v in p.versions.all()],
            [("2.9", False), ("2.10", True)]
            )


    def test_undeleting_a_version_reorders(self):
        """Undeleting a product version reorders the versions."""
        p = self.F.ProductFactory.create()
        self.F.ProductVersionFactory.create(version="2.10", product=p)
        self.F.ProductVersionFactory.create(version="2.9", product=p)
        pv = self.F.ProductVersionFactory.create(version="2.11", product=p)

        pv.delete()
        self.refresh(pv).undelete()

        self.assertEqual(
            [(v.version, v.latest) for v in p.versions.all()],
            [("2.9", False), ("2.10", False), ("2.11", True)]
            )


    @patch("cc.model.ccmodel.datetime")
    def test_reorder_versions_does_not_change_modified_on(self, mock_dt):
        """Updating latest product version does not change modified_on."""
        mock_dt.datetime.utcnow.return_value = datetime(2012, 1, 30)
        pv = self.F.ProductVersionFactory.create()

        mock_dt.datetime.utcnow.return_value = datetime(2012, 1, 31)
        pv.product.reorder_versions()

        self.assertEqual(
            self.refresh(pv).modified_on, datetime(2012, 1, 30))
        self.assertEqual(
            self.refresh(pv.product).modified_on, datetime(2012, 1, 30))


    def test_reorder_versions_does_not_change_modified_by(self):
        """Updating latest product version does not change modified_by."""
        u = self.F.UserFactory.create()
        p = self.F.ProductFactory.create(user=u)
        pv = self.F.ProductVersionFactory.create(product=p, user=u)

        pv.product.reorder_versions()

        self.assertEqual(self.refresh(pv).modified_by, u)
        self.assertEqual(self.refresh(p).modified_by, u)


    def test_instance_being_saved_is_updated(self):
        """Version being saved gets correct order after reorder."""
        p = self.F.ProductFactory.create()
        self.F.ProductVersionFactory.create(version="2.9", product=p)
        pv = self.F.ProductVersionFactory.create(version="2.10", product=p)

        self.assertEqual(pv.order, 2)
        self.assertEqual(pv.latest, True)


    def test_unique_constraint(self):
        """Can't have two versions of same product with same version number."""
        pv = self.F.ProductVersionFactory.create()

        new = self.F.ProductVersionFactory.build(
            product=pv.product, version=pv.version)

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_with_unset_product(self):
        """Unique-check doesn't blow up if product is unset."""
        new = self.model.ProductVersion()

        with self.assertRaises(ValidationError):
            new.full_clean()


    def test_unique_constraint_doesnt_prevent_edit(self):
        """Unique constraint still allows saving an edited existing object."""
        pv = self.F.ProductVersionFactory.create()

        pv.codename = "new codename"

        pv.full_clean()


    def test_unique_constraint_ignores_deleted(self):
        """Deleted version doesn't prevent new with same product, version."""
        pv = self.F.ProductVersionFactory.create()
        pv.delete()

        self.F.ProductVersionFactory.create(version=pv.version, product=pv.product)



class SortByVersionTest(case.DBTestCase):
    """
    Tests ``by_version`` sorting key func for ProductVersions.

    """
    def assertOrder(self, *versions):
        """Assert that ``by_version`` orders given versions as listed."""
        from cc.model.core.models import by_version
        objs = [
            self.F.ProductVersionFactory(version=v) for v in reversed(versions)
            ]
        candidate = [o.version for o in sorted(objs, key=by_version)]

        self.assertEqual(candidate, list(versions))


    def test_numeral_padding(self):
        """Numerals are padded so as to compare numerically."""
        self.assertOrder("2", "11")


    def test_lexicographic(self):
        """Lexicographic ordering."""
        self.assertOrder("aa", "ab")


    def test_mixed_numeral_padding(self):
        """Numerals are padded even when mixed with letters."""
        self.assertOrder("1.1.a2", "1.1.a11")


    def test_pre_release(self):
        """Alpha strings prior to "final" are pre-release versions."""
        self.assertOrder("1.1a", "1.1")
