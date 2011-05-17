from ..builder import ListBuilder
from ..responses import make_locator



environmentgroups = ListBuilder(
    "environmentgroup",
    "environmentgroups",
    "Environmentgroup",
    {
        "companyId": 1,
        "companyLocator": make_locator(id=1, url="companies/1"),
        "environmentTypeId": 1,
        "environmentTypeLocator": make_locator(id=1, url="environmenttypes/1"),
        "description": "",
        "name": "Default Environmentgroup",
        }
    )
