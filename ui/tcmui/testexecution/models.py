"""
Remote objects related to the "documentation" (as opposed to execution) side of
testing.

"""
from ..core.api import RemoteObject, ListObject, fields
from ..products.models import Product
from ..static.fields import StaticData



class TestCycle(RemoteObject):
    product = fields.Locator(Product)
    name = fields.Field()
    description = fields.Field()
    testCycleStatus = StaticData("TESTCYCLESTATUS")
    startDate = fields.Date()
    endDate = fields.Date()


    def __unicode__(self):
        return self.name


    # @@@ broken in API, NullPointerException
    def activate(self, **kwargs):
        self._put(
            relative_url="activate",
            update_from_response=True,
            **kwargs)


    # @@@ broken in API, NullPointerException
    def deactivate(self, **kwargs):
        self._put(
            relative_url="deactivate",
            update_from_response=True,
            **kwargs)



class TestCycleList(ListObject):
    entryclass = TestCycle
    api_name = "testcycles"
    default_url = "testcycles"

    entries = fields.List(fields.Object(TestCycle))
