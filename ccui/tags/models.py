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
from ..core.api import RemoteObject, ListObject, fields, Named
from ..core.models import Company



class Tag(Named, RemoteObject):
    name = fields.Field()
    company = fields.Locator(Company)


    def __unicode__(self):
        return self.name



class TagList(ListObject):
    entryclass = Tag
    api_name = "tags"
    default_url = "tags"

    entries = fields.List(fields.Object(Tag))
