from ..builder import ListBuilder
from ..responses import make_locator



users = ListBuilder(
    "user",
    "users",
    "User",
    {
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "Person",
        "screenName": "test",
        "userStatusId": 1,
        }
    )


permissions = ListBuilder(
    "permission",
    "permissions",
    "Permission",
    {
        "assignable": True,
        "name": "",
        "permissionCode": "PERMISSION_MOCK"
        }
    )
