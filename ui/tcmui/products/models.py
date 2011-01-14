"""
Product-related remote objects.

"""
from ..core import api
from ..core.models import Company


class Product(api.RemoteObject):
    # @@@ identity = api.ResourceIdentity()
    company = api.Locator(Company)
    description = api.Field()
    name = api.Field()



class ProductList(api.ListObject):
    entryclass = Product
    api_name = "products"

    entries = api.List(api.Object(Product))
