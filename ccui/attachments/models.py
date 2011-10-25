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
from ..static.fields import StaticData



class Attachment(Named, RemoteObject):
    name = fields.CharField()
    description = fields.CharField()
    url = fields.CharField()
    size = fields.Field()
    attachmentType = StaticData("ATTACHMENTTYPE", "attachmentTypeId")


    def __unicode__(self):
        return self.name


    def delete(self):
        # to delete an attachment from its canonical URL requires providing an
        # entityID and entityType; simpler to delete it via the entity we got
        # it from.
        source = getattr(self, "linked_from", None)
        if source is None:
            raise ValueError("Cannot delete attachment without source context.")
        return super(Attachment, self).delete(
            url=source._location + "/attachments/" + self.id)



class AttachmentList(ListObject):
    entryclass = Attachment
    api_name = "attachments"
    default_url = "attachments"

    entries = fields.List(fields.Object(Attachment))


    def __iter__(self):
        for att in super(AttachmentList, self).__iter__():
            att.linked_from = self.linked_from
            yield att
