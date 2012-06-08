"""
Tests for ApiKey model.

"""
from mock import patch

from tests import case



class ApiKeyTest(case.DBTestCase):
    """Tests for ApiKey model."""
    def test_unicode(self):
        """Unicode representation is the key."""
        k = self.F.ApiKeyFactory.build(key="12345")

        self.assertEqual(unicode(k), u"12345")


    def test_active(self):
        """Manager has method to return active keys only."""
        self.F.ApiKeyFactory.create(active=False)
        k = self.F.ApiKeyFactory.create(active=True)

        self.assertEqual(list(self.model.ApiKey.objects.active()), [k])


    def test_generate(self):
        """Generate classmethod generates an API key from a UUID."""
        u1 = self.F.UserFactory.create()
        u2 = self.F.UserFactory.create()

        with patch("moztrap.model.core.models.uuid") as mockuuid:
            mockuuid.uuid4.return_value = "foo"

            k = self.model.ApiKey.generate(owner=u1, user=u2)

        self.assertEqual(k.key, "foo")
        self.assertEqual(k.owner, u1)
        self.assertEqual(k.created_by, u2)


    def test_generate_default_creator(self):
        """Generate classmethod can just take a single user."""
        u1 = self.F.UserFactory.create()

        k = self.model.ApiKey.generate(u1)

        self.assertEqual(k.owner, u1)
        self.assertEqual(k.created_by, u1)
