"""
Product-related remote objects.

"""
from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company


class Product(RemoteObject):
    company = fields.Locator(Company)
    description = fields.Field()
    name = fields.Field()



class ProductList(ListObject):
    entryclass = Product
    api_name = "products"
    default_url = "products"

    entries = fields.List(fields.Object(Product))
