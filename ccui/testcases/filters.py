from ..core.filters import LocatorFieldFilter

from .models import TestSuiteList



class TestSuiteFieldFilter(LocatorFieldFilter):
    target = TestSuiteList
