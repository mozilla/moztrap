"""
Tests for ApiKey model.

"""
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
