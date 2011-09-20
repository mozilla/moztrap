"""
Product-related remote objects.

"""
from ..core.api import ListObject, RemoteObject, fields, Named
from ..core.models import Company
from ..core.util import id_for_object
from ..environments.models import EnvironmentGroupList
from ..users.models import Team



class Product(Named, RemoteObject):
    company = fields.Locator(Company)
    description = fields.Field()
    name = fields.Field()

    environmentgroups = fields.Link(EnvironmentGroupList)
    team = fields.Link(Team, api_name="team/members")

    @property
    def testcycles(self):
        from ..testexecution.models import TestCycleList

        return TestCycleList.get(auth=self.auth).filter(product=self)


    non_field_filters = {
        "tester": "teamMemberId",
        "environment": "includedEnvironmentId",
        }


    def __unicode__(self):
        return self.name


    def autogenerate_env_groups(self, environments, envtype=None, **kwargs):
        """
        Autogenerate environment groups for all combinations of given
        ``environments`` (should be an iterable of Environments or Environment
        IDs), optionally generating only groups of type ``envtype`` (should be
        an EnvironmentType with groupType=True, or the ID of one).

        """
        if envtype:
            url = ("environmentgroups/environmenttypes/%s/autogenerate"
                   % id_for_object(envtype))
        else:
            url = "environmentgroups/autogenerate"

        extra_payload = {
            "environmentIds": [id_for_object(e) for e in environments]}

        generated = EnvironmentGroupList()

        self._put(
            relative_url=url,
            extra_payload=extra_payload,
            update_from_response=generated,
            **kwargs)

        return generated



class ProductList(ListObject):
    entryclass = Product
    api_name = "products"
    default_url = "products"

    entries = fields.List(fields.Object(Product))
