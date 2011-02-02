"""
Product-related remote objects.

"""
from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company
from ..core.util import object_or_id
from ..environments.models import EnvironmentGroupList



class Product(RemoteObject):
    company = fields.Locator(Company)
    description = fields.Field()
    name = fields.Field()

    environmentgroups = fields.Link(EnvironmentGroupList)


    def __unicode__(self):
        return self.name


    def autogenerate_env_groups(self, environments, envtype=None, **kwargs):
        if envtype:
            # support either a raw ID or an EnvironmentType object
            try:
                typeid = envtype.identity["@id"]
            except (AttributeError, KeyError):
                typeid = envtype
            url = "environmentgroups/environmenttypes/%s/autogenerate" % typeid
        else:
            url = "environmentgroups/autogenerate"

        extra_payload = {
            "environmentIds": [object_or_id(e) for e in environments]}

        self._put(relative_url=url, extra_payload=extra_payload, **kwargs)



class ProductList(ListObject):
    entryclass = Product
    api_name = "products"
    default_url = "products"

    entries = fields.List(fields.Object(Product))
