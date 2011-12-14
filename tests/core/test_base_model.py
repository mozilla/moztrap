"""
Tests for ``BaseModel`` (and by extension ``BaseManager``,
``NotDeletedManager``, and ``BaseQuerySet``).

These tests use the ``Product`` model, as its a simple model
inherited from ``BaseModel``, and this avoids the need for a
test-only model.

"""
import datetime

from django.test import TestCase

from mock import patch

from ..builders import create_user, create_product, refresh



class BaseModelTestCase(TestCase):
    @property
    def Product(self):
        from cc.core.models import Product
        return Product


    def setUp(self):
        self.user = create_user()

        self.utcnow = datetime.datetime(2011, 12, 13, 22, 39)
        patcher = patch("cc.core.base_model.datetime")
        self.mock_utcnow = patcher.start().datetime.utcnow
        self.mock_utcnow.return_value = self.utcnow
        self.addCleanup(patcher.stop)



class CreateTest(BaseModelTestCase):
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



class SaveTest(BaseModelTestCase):
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



class UpdateTest(BaseModelTestCase):
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



class DeleteTest(BaseModelTestCase):
    def test_queryset_deleted_by_none(self):
        """queryset delete() sets deleted_by to None if not given user."""
        p = create_product()

        self.Product.objects.all().delete()

        self.assertEqual(refresh(p).deleted_by, None)


    def test_queryset_deleted_by(self):
        """queryset delete() sets deleted_by if given user."""
        p = create_product()

        self.Product.objects.all().delete(user=self.user)

        self.assertEqual(refresh(p).deleted_by, self.user)


    def test_queryset_deleted_on(self):
        """queryset delete() sets deleted_on."""
        p = create_product()

        self.Product.objects.all().delete()

        self.assertEqual(refresh(p).deleted_on, self.utcnow)


    def test_deleted_by_none(self):
        """delete() sets deleted_by to None if not given user."""
        p = create_product()

        p.delete()

        self.assertEqual(refresh(p).deleted_by, None)


    def test_deleted_by(self):
        """delete() sets deleted_by if given user."""
        p = create_product()

        p.delete(user=self.user)

        self.assertEqual(refresh(p).deleted_by, self.user)


    def test_deleted_on(self):
        """delete() sets deleted_on."""
        p = create_product()

        p.delete()

        self.assertEqual(refresh(p).deleted_on, self.utcnow)
