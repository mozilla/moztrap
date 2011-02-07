"""
Field types for TCM API.

"""
from posixpath import join

from dateutil import parser
import remoteobjects




class Field(remoteobjects.fields.Field):
    def __init__(self, api_name=None, default=None, api_submit_name=None):
        self.api_submit_name = api_submit_name
        super(Field, self).__init__(api_name, default)


    def install(self, attrname, cls):
        super(Field, self).install(attrname, cls)

        if self.api_submit_name is None:
            self.api_submit_name = self.api_name

        if not self.api_name.startswith("ns1."):
            self.api_name = "ns1.%s" % self.api_name


    def decode(self, value):
        if value == {"@xsi.nil": "true"}:
            value = None
        return super(Field, self).decode(value)


    def submit_data(self, obj):
        if not self.api_submit_name:
            return {}
        value = getattr(obj, self.attrname, None)
        if value is None:
            return {}
        value = self.encode(value)
        if isinstance(value, dict):
            return value
        return {self.api_submit_name: value}



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
    def __init__(self, cls, api_name=None, default=None, api_submit_name=None):
        self.cls = cls
        super(Locator, self).__init__(api_name, default, api_submit_name)


    def install(self, attrname, cls):
        auto_api_name = (self.api_name is None)
        auto_submit_name = (self.api_submit_name is None)

        super(Locator, self).install(attrname, cls)

        if auto_api_name:
            self.api_name = "%sLocator" % self.api_name
        if auto_submit_name:
            self.api_submit_name = "%sId" % self.api_submit_name


    def __get__(self, obj, cls):
        if obj is None:
            return self

        data = super(Locator, self).__get__(obj, cls)

        try:
            if "@url" in data:
                value = None
                linked_id = data.get("@id", None)
                if linked_id and int(linked_id):
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
        if isinstance(value, (list, tuple)):
            value = self.cls(entries=list(value))
        value.put(
            url=join(instance._location, self.api_name),
            version_payload=instance,
            auth=value.auth or instance.auth
            )



List = remoteobjects.fields.List
Object = remoteobjects.fields.Object
