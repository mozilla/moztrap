from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company



class Tag(RemoteObject):
    tag = fields.Field()
    company = fields.Locator(Company)

    name_field = "tag"



class TagList(ListObject):
    entryclass = Tag
    api_name = "tags"
    default_url = "tags"

    entries = fields.List(fields.Object(Tag))
