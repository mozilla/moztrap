from django.core.urlresolvers import reverse

from ..core.finder import Finder, Column
from ..products.models import ProductList
from ..static.status import TestRunStatus, TestCycleStatus
from ..testexecution.models import TestCycleList, TestRunList



class RunTestsFinder(Finder):
    template_base = "runtests/finder"

    columns = [
        Column("products", "_products.html", ProductList, "product"),
        Column("cycles", "_cycles.html", TestCycleList, "testCycle",
               status=TestCycleStatus.ACTIVE),
        Column("runs", "_runs.html", TestRunList, "run",
               status=TestRunStatus.ACTIVE),
        ]


    def child_query_url(self, obj):
        if isinstance(obj, TestRunList.entryclass):
            return reverse(
                "runtests_finder_environments", kwargs={"run_id": obj.id}
                )
        return super(RunTestsFinder, self).child_query_url(obj)
