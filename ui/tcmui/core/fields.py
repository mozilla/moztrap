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



class StaticData(Field):
    """
    A Field whose value is a key to a staticData lookup table. Attribute access
    returns the full CodeValue instance (with id, description, and sortOrder
    attributes.)

    """
    def __init__(self, key, default=None):
        self.key = key
        super(StaticData, self).__init__(None, default)


    def install(self, attrname, cls):
        super(StaticData, self).install(attrname, cls)

        self.api_name = "%sId" % self.api_name


    def __get__(self, obj, cls):
        if obj is None:
            return self

        data = super(StaticData, self).__get__(obj, cls)

        if data:
            from ..static.models import ArrayOfCodeValue
            # @@@ For long lists, it might be better to query by id (if the API
            # allows?).  For short lists, if we cache the entire list, this
            # might be better anyway.
            for code in ArrayOfCodeValue.get(self.key):
                if code.id == data:
                    return code
        return data



List = remoteobjects.fields.List
Object = remoteobjects.fields.Object
