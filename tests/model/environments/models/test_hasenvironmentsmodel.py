"""
Tests for ``HasEnvironmentsModel``.

"""
from tests import case



class HasEnvironmentsModelTest(case.TestCase):
    """Tests for HasEnvironmentsModel base class."""
    @property
    def model_class(self):
        """The abstract model class under test."""
        from cc.model.environments.models import HasEnvironmentsModel
        return HasEnvironmentsModel


    def test_parent(self):
        """parent property is None in base class."""
        t = self.model_class()
        self.assertIsNone(t.parent)


    def test_cascade_envs_to(self):
        """cascade_envs_to returns empty dict in base class."""
        self.assertEqual(self.model_class.cascade_envs_to([], True), {})
