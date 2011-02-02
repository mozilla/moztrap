"""
Field types for TCM API.

"""
from posixpath import join

from dateutil import parser
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
        if value is None:
            return {}
        value = self.encode(value)
        if isinstance(value, dict):
            return value
        return {self.api_submit_name: value}



class Field(FieldMixin, remoteobjects.fields.Field):
    pass



class Date(Field):
    """
    A Date field for when the server is returning a datetime, but we really
    only care about the date.

    """
    def encode(self, value):
        return value.strftime("%Y/%m/%d")


    def decode(self, value):
        return parser.parse(value).date()



class Locator(remoteobjects.fields.AcceptsStringCls, Field):
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
                value = self.cls.get(data["@url"], auth=obj.auth)
                self.__set__(obj, value)
                return value
        except TypeError:
            pass
        return data


    def encode(self, value):
        return value.identity["@id"]



class ResourceIdentity(Field):
    def __init__(self):
        super(ResourceIdentity, self).__init__(api_name="resourceIdentity")


    def encode(self, value):
        ret = {"%s.id" % self.api_submit_name: value["@id"]}
        if "@version" in value:
            ret["%s.version" % self.api_submit_name] = value["@version"]
        return ret



class Link(remoteobjects.fields.Link):
    def __get__(self, instance, owner):
        """
        Generates the RemoteObject for the target resource of this Link.

        """
        if instance._location is None:
            raise AttributeError('Cannot find URL of %s relative to URL-less %s' % (self.cls.__name__, owner.__name__))
        newurl = join(instance._location, self.api_name)
        obj = self.cls.get(newurl, auth=instance.auth)
        obj.auth = instance.auth
        return obj


    def __set__(self, instance, value):
        value.put(
            url=join(instance._location, self.api_name),
            version_payload=instance,
            auth=value.auth or instance.auth
            )



List = remoteobjects.fields.List
Object = remoteobjects.fields.Object
