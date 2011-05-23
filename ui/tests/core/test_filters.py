from mock import Mock
from unittest2 import TestCase



class FilterTestCase(TestCase):
    @property
    def status_field_filter(self):
        if not hasattr(self, "_status_field_filter"):
            from tcmui.core.filters import FieldFilter

            class StatusFieldFilter(FieldFilter):
                options = [
                    (1, "draft"),
                    (2, "active"),
                    (3, "locked"),
                     ]

            self._status_field_filter = StatusFieldFilter

        return self._status_field_filter


    def GET(self, **kwargs):
        from django.utils.datastructures import MultiValueDict
        return MultiValueDict(kwargs)


class TestFilter(FilterTestCase):
    @property
    def filter_class(self):
        from tcmui.core.filters import Filter
        return Filter


    def test_field_iteration(self):
        f = self.filter_class(
            self.GET(status=["draft", "active"]),
            status=self.status_field_filter)

        fields = list(f)
        self.assertEqual(len(fields), 1)
        field = fields[0]
        self.assertEqual(field.name, "status")
        self.assertEqual(field.values, set(["draft", "active"]))


    def test_filter(self):
        f = self.filter_class(
            self.GET(status=["draft", "active"]),
            status=self.status_field_filter)

        list_obj = Mock()
        f.filter(list_obj)

        list_obj.filter.assert_called_with(status=set(["active", "draft"]))



class FieldFilterTest(FilterTestCase):
    def test_iteration(self):
        ff = self.status_field_filter(
            "status", ["1", "2"])

        options = list(ff)

        self.assertEqual(len(options), 3)
        self.assertEqual([o.value for o in options], [1, 2, 3])
        self.assertEqual(
            [o.label for o in options], ["draft", "active", "locked"])
        self.assertEqual(
            [o.selected for o in options], [True, True, False])

    def test_repr(self):
        ff = self.status_field_filter(
            "status", ["draft", "active"])

        self.assertEqual(
            repr(ff),
            "StatusFieldFilter('status', set(['active', 'draft']))")
