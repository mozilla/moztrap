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
    api_name = "externalbugs"

    entries = fields.List(fields.Object(ExternalBug))
