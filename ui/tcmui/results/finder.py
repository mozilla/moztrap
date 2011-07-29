from django.core.urlresolvers import reverse

from ..core.finder import Finder, Column
from ..products.models import ProductList
from ..testexecution.models import (
    TestCycleList, TestRunList, TestRunIncludedTestCaseList)



class ResultsFinder(Finder):
    template_base = "results/finder"

    columns = [
        Column("products", "_products.html", ProductList, "product",
               goto="results_testcycles"),
        Column("cycles", "_cycles.html", TestCycleList, "testCycle",
               goto="results_testruns"),
        Column("runs", "_runs.html", TestRunList, "testRun",
               goto="results_testcases"),
        Column("cases", "_cases.html", TestRunIncludedTestCaseList, "testCase",
               goto="results_testcase_detail"),
        ]


    def goto_url(self, obj):
        model = TestRunIncludedTestCaseList.entryclass
        if isinstance(obj, model):
            return reverse(
                self.columns_by_model[model].goto,
                kwargs={"itc_id": obj.id})
        return super(ResultsFinder, self).goto_url(obj)


    def objects(self, column_name, parent_id=None):
        ret = super(ResultsFinder, self).objects(column_name, parent_id)
        if column_name == "cases":
            for itc in ret:
                itc.name = itc.testCase.name
        return ret


    def child_column_for_obj(self, obj):
        if isinstance(obj, TestRunIncludedTestCaseList.entryclass):
            return "results"
        return super(ResultsFinder, self).child_column_for_obj(obj)
