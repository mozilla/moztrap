"""
User-related remote objects.

"""
import urllib

from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company
from ..static.fields import StaticData



def object_or_id(val):
    """

    """
    try:
        return val.identity["@id"]
    except (AttributeError, KeyError):
        pass

    try:
        return int(val)
    except ValueError:
        pass

    raise ValueError("Values must be RemoteObject instances or integer ids, "
                     "'%r' appears to be neither." % val)



class Permission(RemoteObject):
    assignable = fields.Field()
    name = fields.Field()
    permissionCode = fields.Field()


    def __unicode__(self):
        return self.permissionCode



class PermissionList(ListObject):
    entryclass = Permission
    api_name = "permissions"
    default_url = "users/permissions"

    entries = fields.List(fields.Object(Permission))


    def __unicode__(self):
        return u"%s Permissions" % len(self)



class Role(RemoteObject):
    company = fields.Locator(Company)
    name = fields.Field()


    def __unicode__(self):
        return self.name


    def setpermissions(self, perms, **kwargs):
        payload_data = {"permissionIds": [object_or_id(p) for p in perms]}

        self._put(
            relative_url="permissions",
            extra_payload=payload_data,
            **kwargs)


    def addpermission(self, perm, **kwargs):
        perm_id = object_or_id(perm)

        self._post(
            relative_url="permissions/%s" % perm_id,
            **kwargs)


    def removepermission(self, perm, **kwargs):
        perm_id = object_or_id(perm)

        self._delete(
            relative_url="permissions/%s" % perm_id,
            **kwargs)



class RoleList(ListObject):
    entryclass = Role
    api_name = "roles"
    default_url = "users/roles"

    entries = fields.List(fields.Object(Role))


    def __unicode__(self):
        return u"%s Roles" % len(self)



class User(RemoteObject):
    company = fields.Locator(Company)
    email = fields.Field()
    firstName = fields.Field()
    lastName = fields.Field()
    password = fields.Field()
    screenName = fields.Field()
    userStatus = StaticData("USERSTATUS")

    roles = fields.Link(RoleList)

    def __unicode__(self):
        return self.screenName


    @classmethod
    def current(cls, **kwargs):
        kwargs["url"] = "users/current"
        return cls.get(**kwargs)


    def activate(self, **kwargs):
        self._put(relative_url="activate", **kwargs)


    def deactivate(self, **kwargs):
        self._put(relative_url="deactivate", **kwargs)


    def emailchange(self, newemail, **kwargs):
        self._put(
            relative_url="emailchange/%s" % urllib.quote(newemail),
            **kwargs
        )


    def emailconfirm(self, **kwargs):
        self._put(relative_url="emailconfirm", **kwargs)


    def passwordchange(self, newpassword, **kwargs):
        self._put(
            relative_url="passwordchange/%s" % urllib.quote(newpassword),
            **kwargs
        )


    def login(self, **kwargs):
        self._put(
            url="users/login",
            version_payload=False,
            default_content_type="application/json",
            **kwargs
            )


    def logout(self, **kwargs):
        self._put(
            url="users/logout",
            version_payload=False,
            default_content_type="application/json",
            **kwargs
            )


    def setroles(self, roles, **kwargs):
        payload_data = {"roleIds": [object_or_id(r) for r in roles]}

        self._put(
            relative_url="roles",
            extra_payload=payload_data,
            **kwargs)



class UserList(ListObject):
    entryclass = User
    api_name = "users"
    default_url = "users"

    entries = fields.List(fields.Object(User))


    def __unicode__(self):
        return u"%s Users" % len(self)
