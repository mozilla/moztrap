"""
User-related remote objects.

"""
import urllib

from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company
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


    def __unicode__(self):
        return u"%s Permissions" % len(self)



class Role(RemoteObject):
    company = fields.Locator(Company)
    name = fields.Field()


    def __unicode__(self):
        return self.name


    def setpermissions(self, perms, **kwargs):
        payload_data = {"permissionIds": [p.identity["@id"] for p in perms]}
        self._put(
            relative_url="permissions",
            extra_payload=payload_data,
            update_from_response=False,
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
            update_from_response=False,
            default_content_type="application/json",
            **kwargs
            )


    def logout(self, **kwargs):
        self._put(
            url="users/logout",
            version_payload=False,
            update_from_response=False,
            default_content_type="application/json",
            **kwargs
            )


    def setroles(self, roles, **kwargs):
        roleIds = []
        for r in roles:
            try:
                roleIds.append(r.identity["@id"])
            except (AttributeError, KeyError):
                pass
            else:
                continue

            try:
                roleIds.append(int(r))
            except ValueError:
                pass
            else:
                continue

            raise ValueError("Values passed to User.setroles must be integer "
                             "ids or Role instances; %r appears to be neither."
                             % r)

        payload_data = {"roleIds": roleIds}
        self._put(
            relative_url="roles",
            extra_payload=payload_data,
            update_from_response=False,
            **kwargs)



class UserList(ListObject):
    entryclass = User
    api_name = "users"
    default_url = "users"

    entries = fields.List(fields.Object(User))


    def __unicode__(self):
        return u"%s Users" % len(self)
