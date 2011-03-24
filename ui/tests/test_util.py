from unittest2 import TestCase

from tcmui.util.enum import Enum



class EnumTest(TestCase):
    def _make_enum(self):
        class Test(Enum):
            ACTIVE = 1
            DRAFT = 2

        return Test


    def test_rejects_duplicate_values(self):
        with self.assertRaises(ValueError) as cm:
            class Bad(Enum):
                ACTIVE = 1
                DRAFT = 1

        self.assertIn("1", str(cm.exception))


    def test_attribute_access(self):
        Test = self._make_enum()
        self.assertEqual(Test.ACTIVE, 1)


    def test_reverse_access(self):
        Test = self._make_enum()
        self.assertEqual(Test[1], "ACTIVE")
