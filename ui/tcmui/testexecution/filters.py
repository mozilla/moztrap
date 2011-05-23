from ..core.filters import LocatorFieldFilter

from .models import TestCycleList, TestRunList



class TestCycleFieldFilter(LocatorFieldFilter):
    target = TestCycleList



class TestRunFieldFilter(LocatorFieldFilter):
    target = TestRunList
