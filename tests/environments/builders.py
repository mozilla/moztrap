from ..builder import ListBuilder
from ..responses import make_locator, make_boolean



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



environmenttypes = ListBuilder(
    "environmenttype",
    "environmenttypes",
    "Environmenttype",
    {
        "companyId": 1,
        "companyLocator": make_locator(id=1, url="companies/1"),
        "groupType": False,
        "parentEnvironmentTypeId": make_boolean(None),
        "parentEnvironmentTypeLocator": make_boolean(None),
        "sortOrder": 0,
        "name": "Default Environmenttype",
        }
    )



environments = ListBuilder(
    "environment",
    "environments",
    "Environment",
    {
        "companyId": 1,
        "companyLocator": make_locator(id=1, url="companies/1"),
        "environmentTypeId": 1,
        "environmentTypeLocator": make_locator(id=1, url="environmenttypes/1"),
        "name": "Default Environment",
        }
    )
