"""
Field types for TCM API.

"""
import remoteobjects



class FieldMixin(object):
    def install(self, attrname, cls):
        super(FieldMixin, self).install(attrname, cls)

        self.api_name = "ns1.%s" % self.api_name


    def decode(self, value):
        if value == {"@xsi.nil": "true"}:
            value = None
        return super(FieldMixin, self).decode(value)



class Field(FieldMixin, remoteobjects.fields.Field):
    pass



class Locator(Field):
    """
    A Field type to correspond to the Locator data returned by the API for
    linked object IDs; e.g. companyLocator. Accessing the attribute returns an
    instance of the actual linked object.

    """
    def __init__(self, cls, api_name=None, default=None):
        self.cls = cls
        super(Locator, self).__init__(api_name, default)


    def install(self, attrname, cls):
        super(Locator, self).install(attrname, cls)

        self.api_name = "%sLocator" % self.api_name


    def __get__(self, obj, cls):
        if obj is None:
            return self

        data = super(Locator, self).__get__(obj, cls)

        if data and "@url" in data:
            return self.cls.get(data["@url"])
        return data



class ResourceIdentity(Field):
    def __init__(self):
        super(ResourceIdentity, self).__init__(api_name="resourceIdentity")



List = remoteobjects.fields.List
Object = remoteobjects.fields.Object
