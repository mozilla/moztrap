# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
User-related remote objects.

"""
import urllib
from posixpath import join

from ..core.api import RemoteObject, Activatable, ListObject, fields, Named
from ..core.decorators import as_admin
from ..core.models import Company
from ..core.util import id_for_object
from ..static.fields import StaticData



class Permission(Named, RemoteObject):
    assignable = fields.Field()
    name = fields.CharField()
    permissionCode = fields.Field()


    def __unicode__(self):
        return self.permissionCode



class PermissionList(ListObject):
    entryclass = Permission
    api_name = "permissions"
    default_url = "users/permissions"

    entries = fields.List(fields.Object(Permission))



class Role(Named, RemoteObject):
    company = fields.Locator(Company)
    name = fields.CharField()

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
    email = fields.CharField()
    firstName = fields.CharField()
    lastName = fields.CharField()
    password = fields.CharField()
    screenName = fields.CharField()
    status = StaticData("USERSTATUS", "userStatusId")

    roles = fields.Link(RoleList)
    permissions = fields.Link(PermissionList)

    name_field = "screenName"

    def __unicode__(self):
        return self.screenName


    @classmethod
    def current(cls, **kwargs):
        kwargs["url"] = "users/current"
        auth = kwargs.get("auth")
        kwargs.setdefault("cache", auth.userid if auth else False)
        return cls.get(**kwargs)


    @property
    @as_admin
    def permissionCodes(self):
        return [p.permissionCode for p in self.permissions]


    def emailchange(self, newemail, **kwargs):
        self._put(
            relative_url="emailchange/%s" % urllib.quote(newemail),
            update_from_response=True,
            **kwargs)


    def emailconfirm(self, **kwargs):
        self._put(
            relative_url="emailconfirm",
            update_from_response=True,
            **kwargs)


    def passwordchange(self, newpassword, **kwargs):
        self._put(
            relative_url="passwordchange/%s" % urllib.quote(newpassword),
            update_from_response=True,
            **kwargs
        )


    def login(self, **kwargs):
        """
        Returns the token cookie that can be used for further logins.

        """
        response = self._put(
            url="users/login",
            version_payload=False,
            default_content_type="application/json",
            **kwargs
            )
        # Work around httplib2's broken multiple-header handling
        # http://code.google.com/p/httplib2/issues/detail?id=90
        # This will break if a cookie value contains commas.
        cookies = [c.split(";")[0].strip() for c in
                   response["set-cookie"].split(",")]
        return [c for c in cookies if c.startswith("USERTOKEN=")][0]


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



class Team(UserList):
    def roles_for(self, user, roles=None):
        url = join(self._location.split("?")[0], user.id, "roles")
        if roles is None:
            return RoleList.get(url, auth=self.auth)
        if isinstance(roles, (list, tuple, set)):
            roles = RoleList(entries=list(roles))
        roles.put(
            url=url,
            version_payload=self.linked_from,
            auth=roles.auth or self.auth
            )
