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
