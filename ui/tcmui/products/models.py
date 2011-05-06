"""
Product-related remote objects.

"""
from django.core.urlresolvers import reverse

from ..core.api import ListObject, RemoteObject, fields
from ..core.models import Company
from ..core.util import id_for_object
from ..environments.models import EnvironmentGroupList
from ..users.models import Team



class Product(RemoteObject):
    company = fields.Locator(Company)
    description = fields.Field()
    name = fields.Field()

    environmentgroups = fields.Link(EnvironmentGroupList)
    team = fields.Link(Team, api_name="team/members")


    def __unicode__(self):
        return self.name


    def get_absolute_url(self):
        return reverse("cycles", kwargs={"product_id": self.id})


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

        self._put(relative_url=url, extra_payload=extra_payload, **kwargs)



class ProductList(ListObject):
    entryclass = Product
    api_name = "products"
    default_url = "products"

    entries = fields.List(fields.Object(Product))
