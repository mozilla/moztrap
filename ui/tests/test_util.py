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


    def test_inheritance(self):
        Test = self._make_enum()
        class New(Test):
            ARCHIVED = 3

        self.assertEqual(New.ACTIVE, 1)
        self.assertEqual(New.ARCHIVED, 3)


    def test_inheritance_keeps_unique(self):
        Test = self._make_enum()
        with self.assertRaises(ValueError):
            class New(Test):
                ARCHIVED = 1


    def test_multi_inheritance_keeps_unique(self):
        Test = self._make_enum()
        class Base2(Enum):
            OTHER = 1

        with self.assertRaises(ValueError):
            class New(Test, Base2):
                ARCHIVED = 3
