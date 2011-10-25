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
