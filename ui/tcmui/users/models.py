"""
User-related remote objects.

"""
import urllib

from ..core.api import RemoteObject, Activatable, ListObject, fields
from ..core.decorators import as_admin
from ..core.models import Company
from ..core.util import id_for_object
from ..static.fields import StaticData



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



class Role(RemoteObject):
    company = fields.Locator(Company)
    name = fields.Field()

    permissions = fields.Link(PermissionList)


    def __unicode__(self):
        return self.name


    def addpermission(self, perm, **kwargs):
        self._post(
            relative_url="permissions/%s" % id_for_object(perm),
            **kwargs)


    def removepermission(self, perm, **kwargs):
        self._delete(
            relative_url="permissions/%s" % id_for_object(perm),
            **kwargs)



class RoleList(ListObject):
    entryclass = Role
    api_name = "roles"
    default_url = "users/roles"

    entries = fields.List(fields.Object(Role))



class User(Activatable, RemoteObject):
    company = fields.Locator(Company)
    email = fields.Field()
    firstName = fields.Field()
    lastName = fields.Field()
    password = fields.Field()
    screenName = fields.Field()
    userStatus = StaticData("USERSTATUS")

    roles = fields.Link(RoleList)
    permissions = fields.Link(PermissionList)

    def __unicode__(self):
        return self.screenName


    @classmethod
    def current(cls, **kwargs):
        kwargs["url"] = "users/current"
        return cls.get(**kwargs)


    @property
    @as_admin
    def permissionCodes(self):
        return [p.permissionCode for p in self.permissions]


    def emailchange(self, newemail, **kwargs):
        self._put(
            relative_url="emailchange/%s" % urllib.quote(newemail),
            **kwargs)


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



class UserList(ListObject):
    entryclass = User
    api_name = "users"
    default_url = "users"

    entries = fields.List(fields.Object(User))
