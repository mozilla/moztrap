from ..core.filters import RelatedFieldFilter

from .models import TestCycleList, TestRunList



class TestCycleFieldFilter(RelatedFieldFilter):
    target = TestCycleList



class TestRunFieldFilter(RelatedFieldFilter):
    target = TestRunList
