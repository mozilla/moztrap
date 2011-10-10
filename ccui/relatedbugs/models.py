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
from ..core.api import RemoteObject, ListObject, fields



class ExternalBug(RemoteObject):
    url = fields.Field()
    externalIdentifier = fields.Field()


    def __unicode__(self):
        return self.url


    @property
    def is_url(self):
        return "://" in self.url



class ExternalBugList(ListObject):
    entryclass = ExternalBug
    default_url = "externalbugs"
    api_name = "externalbugs"

    entries = fields.List(fields.Object(ExternalBug))
