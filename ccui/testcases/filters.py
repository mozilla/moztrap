from ..core.filters import RelatedFieldFilter

from .models import TestSuiteList



class TestSuiteFieldFilter(RelatedFieldFilter):
    target = TestSuiteList
