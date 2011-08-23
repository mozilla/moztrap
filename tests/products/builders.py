from ..builder import ListBuilder
from ..responses import make_locator



products = ListBuilder(
    "product",
    "products",
    "Product",
    {
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "description": "",
        "name": "Default Product",
        }
    )
