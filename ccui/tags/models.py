from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company


# @@@ https://bugzilla.mozilla.org/show_bug.cgi?id=690373
class MightBeAListField(fields.Field):
    def decode(self, value):
        ret = super(MightBeAListField, self).decode(value)
        if isinstance(ret, list):
            ret = ret[0]
        return ret


class Tag(RemoteObject):
    tag = MightBeAListField()
    company = fields.Locator(Company)

    name_field = "tag"


    def __unicode__(self):
        return self.tag



class TagList(ListObject):
    entryclass = Tag
    api_name = "tags"
    default_url = "tags"

    entries = fields.List(fields.Object(Tag))
