"""
Field types for TCM API.

"""
import remoteobjects



class FieldMixin(object):
    def install(self, attrname, cls):
        super(FieldMixin, self).install(attrname, cls)

        self.api_submit_name = self.api_name

        if not self.api_name.startswith("ns1."):
            self.api_name = "ns1.%s" % self.api_name


    def decode(self, value):
        if value == {"@xsi.nil": "true"}:
            value = None
        return super(FieldMixin, self).decode(value)


    def submit_data(self, obj):
        value = getattr(obj, self.attrname, None)
        if value is not None:
            return {self.api_submit_name: self.encode(value)}
        return {}



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

        self.api_submit_name = "%sId" % self.api_submit_name
        self.api_name = "%sLocator" % self.api_name


    def __get__(self, obj, cls):
        if obj is None:
            return self

        data = super(Locator, self).__get__(obj, cls)

        try:
            if "@url" in data:
                value = self.cls.get(data["@url"])
                self.__set__(obj, value)
                return value
        except TypeError:
            pass
        return data

    def __set__(self, obj, value):
        super(Locator, self).__set__(obj, value)
        obj.__dict__[self.api_submit_name] = value.identity["@id"]

    def submit_data(self, obj):
        value = getattr(obj, self.api_submit_name, None)
        if value is not None:
            return {self.api_submit_name: self.encode(value)}
        return {}



class ResourceIdentity(Field):
    def __init__(self):
        super(ResourceIdentity, self).__init__(api_name="resourceIdentity")


    def submit_data(self, obj):
        try:
            d = super(ResourceIdentity, self).submit_data(
                obj
            )[self.api_submit_name]
            if d:
                return {
                    "%s.id" % self.api_submit_name: d["@id"],
                    "%s.version" % self.api_submit_name: d["@version"],
                }
        except KeyError:
            pass
        return {}



List = remoteobjects.fields.List
Object = remoteobjects.fields.Object
