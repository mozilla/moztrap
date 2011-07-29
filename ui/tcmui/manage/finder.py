from ..core.finder import Finder, Column
from ..products.models import ProductList
from ..testcases.models import TestSuiteList
from ..testexecution.models import TestCycleList, TestRunList



class ManageFinder(Finder):
    template_base = "manage/finder"

    columns = [
        Column("products", "_products.html", ProductList, "product",
               goto="manage_testcycles"),
        Column("cycles", "_cycles.html", TestCycleList, "testCycle",
               goto="manage_testruns"),
        Column("runs", "_runs.html", TestRunList, "run",
               goto="manage_testsuites"),
        Column("suites", "_suites.html", TestSuiteList, "suite",
               goto="manage_testcases"),
        ]
