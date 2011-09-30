from ..builder import ListBuilder
from ..responses import make_locator



tags = ListBuilder(
    "tag",
    "tags",
    "Tag",
    {
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "tag": "Default Tag",
        }
    )
