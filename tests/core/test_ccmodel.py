# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
Tests for ``CCModel`` (and by extension ``CCManager``,
``NotDeletedCCManager``, and ``CCQuerySet``).

These tests use the ``Product`` model (and ``Suite`` for cascade-delete
tests), as its a simple model inherited from ``CCModel``, and this
avoids the need for a test-only model.

"""
import datetime

from django.test import TestCase

from mock import patch

from ..utils import refresh
from .. import factories as F



class CCModelTestCase(TestCase):
    """Common base class for CCModel tests."""
    @property
    def Product(self):
        """Returns the Product model."""
        from cc.core.models import Product
        return Product


    def setUp(self):
        """Creates ``self.user`` for use by all tests."""
        self.user = F.UserFactory.create()



class CCModelMockNowTestCase(CCModelTestCase):
    """Base class for CCModel tests that need "now" mocked."""
    def setUp(self):
        """Mocks datetime.utcnow() with datetime in self.utcnow."""
        super(CCModelMockNowTestCase, self).setUp()

        self.utcnow = datetime.datetime(2011, 12, 13, 22, 39)
        patcher = patch("cc.core.ccmodel.datetime")
        self.mock_utcnow = patcher.start().datetime.utcnow
        self.mock_utcnow.return_value = self.utcnow
        self.addCleanup(patcher.stop)



class CreateTest(CCModelMockNowTestCase):
    """Tests for (created/modified)_(on/by) when using Model.objects.create."""
    def test_created_by_none(self):
        """If ``user`` is not given to create(), created_by is None."""
        p = self.Product.objects.create(name="Foo")

        self.assertEqual(p.created_by, None)


    def test_created_by(self):
        """If ``user`` is given to create(), created_by is set."""
        p = self.Product.objects.create(name="Foo", user=self.user)

        self.assertEqual(p.created_by, self.user)


    def test_new_modified_by_none(self):
        """If ``user`` is not given to create(), modified_by is None."""
        p = self.Product.objects.create(name="Foo")

        self.assertEqual(p.modified_by, None)


    def test_new_modified_by(self):
        """If ``user`` is given to create(), modified_by is set."""
        p = self.Product.objects.create(name="Foo", user=self.user)

        self.assertEqual(p.modified_by, self.user)


    def test_created_on(self):
        """create() method sets created_on."""
        p = self.Product.objects.create(name="Foo")

        self.assertEqual(p.created_on, self.utcnow)


    def test_new_modified_on(self):
        """create() method sets modified_on."""
        p = self.Product.objects.create(name="Foo")

        self.assertEqual(p.modified_on, self.utcnow)



class SaveTest(CCModelMockNowTestCase):
    """Tests for (created/modified)_(on/by) when using instance.save."""
    def test_created_by_none(self):
        """If ``user`` is not given to new obj save(), created_by is None."""
        p = self.Product(name="Foo")
        p.save()

        self.assertEqual(p.created_by, None)


    def test_created_by(self):
        """If ``user`` is given to new obj save(), created_by is set."""
        p = self.Product(name="Foo")
        p.save(user=self.user)

        self.assertEqual(p.created_by, self.user)


    def test_new_modified_by_none(self):
        """If ``user`` is not given to new obj save(), modified_by is None."""
        p = self.Product(name="Foo")
        p.save()

        self.assertEqual(p.modified_by, None)


    def test_new_modified_by(self):
        """If ``user`` is given to new obj save(), modified_by is set."""
        p = self.Product(name="Foo")
        p.save(user=self.user)

        self.assertEqual(p.modified_by, self.user)


    def test_created_on(self):
        """save() method sets created_on."""
        p = self.Product(name="Foo")
        p.save()

        self.assertEqual(p.created_on, self.utcnow)


    def test_new_modified_on(self):
        """save() method sets modified_on for new object."""
        p = self.Product(name="Foo")
        p.save()

        self.assertEqual(p.modified_on, self.utcnow)


    def test_modified_by_none(self):
        """If ``user`` is not given to save(), modified_by is set to None."""
        p = self.Product.objects.create(name="Foo", user=self.user)
        p.save()

        self.assertEqual(p.modified_by, None)


    def test_modified_by(self):
        """If ``user`` is given to save(), modified_by is set."""
        p = self.Product.objects.create(name="Foo")
        p.save(user=self.user)

        self.assertEqual(p.modified_by, self.user)


    def test_modified_on(self):
        """save() method sets modified_on for existing object."""
        p = self.Product.objects.create(name="Foo")
        new_now = datetime.datetime(2012, 1, 1, 12, 0)
        self.mock_utcnow.return_value = new_now
        p.save()

        self.assertEqual(p.modified_on, new_now)



class UpdateTest(CCModelMockNowTestCase):
    """Tests for modified_(by/on) when using queryset.update."""
    def test_modified_by_none(self):
        """queryset update() sets modified_by to None if not given user."""
        p = self.Product.objects.create(name="Foo", user=self.user)

        self.Product.objects.update(name="Bar")

        self.assertEqual(refresh(p).modified_by, None)


    def test_modified_by(self):
        """queryset update() sets modified_by if given user."""
        p = self.Product.objects.create(name="Foo")

        self.Product.objects.update(name="Bar", user=self.user)

        self.assertEqual(refresh(p).modified_by, self.user)


    def test_modified_on(self):
        """queryset update() sets modified_on."""
        p = self.Product.objects.create(name="Foo")
        new_now = datetime.datetime(2012, 1, 1, 12, 0)
        self.mock_utcnow.return_value = new_now

        self.Product.objects.update(name="Bar")

        self.assertEqual(refresh(p).modified_on, new_now)



class DeleteTest(CCModelMockNowTestCase):
    """Tests for deleted_(by/on) when using instance.delete or qs.delete."""
    def test_queryset_deleted_by_none(self):
        """queryset delete() sets deleted_by to None if not given user."""
        p = F.ProductFactory.create()

        self.Product.objects.all().delete()

        self.assertEqual(refresh(p).deleted_by, None)


    def test_queryset_deleted_by(self):
        """queryset delete() sets deleted_by if given user."""
        p = F.ProductFactory.create()

        self.Product.objects.all().delete(user=self.user)

        self.assertEqual(refresh(p).deleted_by, self.user)


    def test_queryset_deleted_on(self):
        """queryset delete() sets deleted_on."""
        p = F.ProductFactory.create()

        self.Product.objects.all().delete()

        self.assertEqual(refresh(p).deleted_on, self.utcnow)


    def test_deleted_by_none(self):
        """delete() sets deleted_by to None if not given user."""
        p = F.ProductFactory.create()

        p.delete()

        self.assertEqual(refresh(p).deleted_by, None)


    def test_deleted_by(self):
        """delete() sets deleted_by if given user."""
        p = F.ProductFactory.create()

        p.delete(user=self.user)

        self.assertEqual(refresh(p).deleted_by, self.user)


    def test_deleted_on(self):
        """delete() sets deleted_on."""
        p = F.ProductFactory.create()

        p.delete()

        self.assertEqual(refresh(p).deleted_on, self.utcnow)



class CascadeDeleteTest(CCModelTestCase):
    """Tests for cascading soft-delete."""
    def test_queryset_deleted_by_none(self):
        """queryset delete() sets deleted_by None if no user on cascade."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)

        self.Product.objects.all().delete()

        self.assertEqual(refresh(s).deleted_by, None)


    def test_queryset_deleted_by(self):
        """queryset delete() sets deleted_by to given user on cascade."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)

        self.Product.objects.all().delete(user=self.user)

        self.assertEqual(refresh(s).deleted_by, self.user)


    def test_queryset_deleted_on(self):
        """qs delete() sets deleted_on to same time as parent on cascade."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)

        self.Product.objects.all().delete()

        p = refresh(p)
        s = refresh(s)
        self.assertIsNot(p.deleted_on, None)

        self.assertEqual(s.deleted_on, p.deleted_on)


    def test_deleted_by_none(self):
        """delete() sets deleted_by None if no user on cascade."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)

        p.delete()

        self.assertEqual(refresh(s).deleted_by, None)


    def test_deleted_by(self):
        """delete() sets deleted_by to given user on cascade."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)

        p.delete(user=self.user)

        self.assertEqual(refresh(s).deleted_by, self.user)


    def test_deleted_on(self):
        """delete() sets deleted_on to same time as parent on cascade."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)

        p.delete()

        p = refresh(p)
        s = refresh(s)
        self.assertIsNot(p.deleted_on, None)

        self.assertEqual(s.deleted_on, p.deleted_on)


    def test_no_cascade_redelete(self):
        """cascade delete won't update deleted-on for previously deleted."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)
        # need to patch utcnow because MySQL doesn't give us better than
        # one-second resolution on datetimes.
        with patch("cc.core.ccmodel.datetime") as mock_dt:
            mock_dt.datetime.utcnow.return_value = datetime.datetime(
                2011, 12, 13, 10, 23, 58)
            s.delete()
            # ... a day later...
            mock_dt.datetime.utcnow.return_value = datetime.datetime(
                2011, 12, 14, 9, 18, 22)
            p.delete()

        self.assertNotEqual(refresh(s).deleted_on, refresh(p).deleted_on)



class UndeleteMixin(object):
    """Utility assertions mixin for undelete tests."""
    def assertNotDeleted(self, obj):
        self.assertEqual(obj.deleted_on, None)
        self.assertEqual(obj.deleted_by, None)



class UndeleteTest(UndeleteMixin, CCModelTestCase):
    """Tests for undelete using instance.undelete or qs.undelete."""
    def test_instance(self):
        """instance.undelete() undeletes an instance."""
        p = F.ProductFactory.create()
        p.delete()

        p.undelete()

        self.assertNotDeleted(p)


    def test_queryset(self):
        """qs.undelete() undeletes all objects in the queryset."""
        p = F.ProductFactory.create()
        p.delete()

        self.Product.everything.all().undelete()

        self.assertNotDeleted(refresh(p))



class CascadeUndeleteTest(UndeleteMixin, CCModelTestCase):
    """Tests for cascading undelete."""
    def test_instance(self):
        """Undeleting an instance also undeletes cascade-deleted dependents."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)
        p.delete()
        p = refresh(p)

        p.undelete()

        self.assertNotDeleted(refresh(s))


    def test_queryset(self):
        """Undeleting a queryset also undeletes cascade-deleted dependents."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)
        p.delete()

        self.Product.everything.all().undelete()

        self.assertNotDeleted(refresh(s))


    def test_cascade_limited(self):
        """Undelete only cascades to objs cascade-deleted with that object."""
        p = F.ProductFactory.create()
        s = F.SuiteFactory.create(product=p)
        # need to patch utcnow because MySQL doesn't give us better than
        # one-second resolution on datetimes.
        with patch("cc.core.ccmodel.datetime") as mock_dt:
            mock_dt.datetime.utcnow.return_value = datetime.datetime(
                2011, 12, 13, 10, 23, 58)
            s.delete()
            # ... a day later ...
            mock_dt.datetime.utcnow.return_value = datetime.datetime(
                2011, 12, 14, 9, 18, 22)
            p.delete()

        refresh(p).undelete()

        self.assertIsNot(refresh(s).deleted_on, None)



class TeamModelTest(TestCase):
    """Tests for TeamModel base class."""
    @property
    def TeamModel(self):
        from cc.core.ccmodel import TeamModel
        return TeamModel


    def test_parent(self):
        """parent property is not implemented in base class."""
        t = self.TeamModel()
        with self.assertRaises(NotImplementedError):
            t.parent
