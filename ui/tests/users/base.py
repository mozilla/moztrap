from ..utils import ResourceTestCase



class UserTestCase(ResourceTestCase):
    RESOURCE_DEFAULTS = {
        "companyId": 1,
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "Person",
        "screenName": "test",
        "userStatusId": 1,
        }


    RESOURCE_NAME = "user"
    RESOURCE_NAME_PLURAL = "users"


    def get_resource_class(self):
        from tcmui.users.models import User
        return User


    def get_resource_list_class(self):
        from tcmui.users.models import UserList
        return UserList



