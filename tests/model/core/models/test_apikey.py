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
