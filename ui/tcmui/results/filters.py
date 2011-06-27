from ..static import filters as status_filters
from ..testcases.filters import TestSuiteFieldFilter
from ..testexecution.filters import TestCycleFieldFilter, TestRunFieldFilter



class NonDraftTestCycleStatusFilter(status_filters.TestCycleStatusFilter):
    options = [
        (k, v) for k, v
        in status_filters.TestCycleStatusFilter.options
        if v != "draft"]



class NonDraftTestRunStatusFilter(status_filters.TestRunStatusFilter):
    options = [
        (k, v) for k, v
        in status_filters.TestRunStatusFilter.options
        if v != "draft"]



class NonDraftTestCaseStatusFilter(status_filters.TestCaseStatusFilter):
    options = [
        (k, v) for k, v
        in status_filters.TestCaseStatusFilter.options
        if v != "draft"]



class NonDraftTestCycleFieldFilter(TestCycleFieldFilter):
    target_filters = {"status": [2, 3]}



class NonDraftTestRunFieldFilter(TestRunFieldFilter):
    target_filters = {"status": [2, 3]}



class NonDraftTestSuiteFieldFilter(TestSuiteFieldFilter):
    target_filters = {"status": [2, 3]}
