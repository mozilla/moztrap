"""
Field types for TCM API.

"""
from posixpath import join

from dateutil import parser
import remoteobjects

from .auth import admin



class Field(remoteobjects.fields.Field):
    api_filter_name = None


    def __init__(self, api_name=None, default=None, api_submit_name=None):
        self.api_submit_name = api_submit_name
        super(Field, self).__init__(api_name, default)


    def install(self, attrname, cls):
        super(Field, self).install(attrname, cls)

        if self.api_submit_name is None:
            self.api_submit_name = self.api_name

        if self.api_filter_name is None:
            self.api_filter_name = self.api_name

        if not (self.api_name.startswith("ns1.") or
                self.api_name.startswith("@")):
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
        encoded = self.encode(value)
        if isinstance(encoded, dict) and encoded != value:
            return encoded
        return {self.api_submit_name: encoded}



class Date(Field):
    """
    A Date field for when the server is returning a datetime, but we really
    only care about the date.

    """
    def encode(self, value):
        return super(Date, self).encode(value.strftime("%Y/%m/%d"))


    def decode(self, value):
        decoded = super(Date, self).decode(value)
        if decoded:
            return parser.parse(decoded).date()
        return decoded



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

        if auto_api_name and not self.api_name.endswith("Locator"):
            self.api_name = "%sLocator" % self.api_name
        if self.api_filter_name and not self.api_filter_name.endswith("Id"):
            self.api_filter_name = "%sId" % self.api_filter_name
        if auto_submit_name and not self.api_submit_name.endswith("Id"):
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
                    value.__dict__["identity"] = data
                self.__set__(obj, value)
                return value
        except TypeError:
            pass
        return data


    def encode(self, value):
        return value.identity["@id"]



class ResourceIdentity(Field):
    api_filter_name = False

    def __init__(self):
        super(ResourceIdentity, self).__init__(api_name="resourceIdentity")


    def encode(self, value):
        if "@version" in value:
            return {"originalVersionId": value["@version"]}
        return {}



class UserID(remoteobjects.fields.AcceptsStringCls, Field):
    """
    A Field type that can find a User object based on just the ID; used by
    Timeline.

    """
    def __init__(self, api_name=None, default=None):
        self.cls = "User"
        super(UserID, self).__init__(api_name, default, api_submit_name=False)


    def __get__(self, obj, cls):
        if obj is None:
            return self

        data = super(UserID, self).__get__(obj, cls)

        if isinstance(data, self.cls):
            return data

        try:
            # @@@ PERMISSION_USER_ACCOUNT_VIEW doesn't work, using admin
            value = self.cls.get(join("users", str(int(data))), auth=admin)
            self.__set__(obj, value)
            return value
        except ValueError:
            pass
        return data



class Timeline(remoteobjects.dataobject.DataObject):
    createDate = Date("@createDate")
    createdBy = UserID("@createdBy")
    lastChangeDate = Date("@lastChangeDate")
    lastChangedBy = UserID("@lastChangedBy")



class TimelineField(Field):
    api_filter_name = False


    def __init__(self):
        super(TimelineField, self).__init__(
            api_name="timeline",
            api_submit_name=False)


    def decode(self, value):
        value = super(TimelineField, self).decode(value)
        if value:
            return Timeline.from_dict(value)
        return value


    def __get__(self, obj, cls):
        if obj is None:
            return self

        t = super(TimelineField, self).__get__(obj, cls)
        t.auth = obj.auth

        return t



class Link(remoteobjects.fields.Link):
    def __init__(self, *args, **kwargs):
        self.cache = kwargs.pop("cache", None)
        super(Link, self).__init__(*args, **kwargs)


    def __get__(self, instance, owner):
        """
        Generates the RemoteObject for the target resource of this Link.

        """
        if instance._location is None:
            raise AttributeError('Cannot find URL of %s relative to URL-less %s' % (self.cls.__name__, owner.__name__))
        newurl = join(instance._location, self.api_name)
        kwargs = {"auth": instance.auth}
        if self.cache is not None:
            kwargs["cache"] = self.cache
        obj = self.cls.get(newurl, **kwargs)
        obj.auth = instance.auth
        obj.linked_from = instance
        return obj


    def __set__(self, instance, value):
        if isinstance(value, (list, tuple, set)):
            value = self.cls(entries=list(value))
        value.put(
            url=join(instance._location, self.api_name),
            version_payload=instance,
            auth=value.auth or instance.auth
            )



List = remoteobjects.fields.List
Object = remoteobjects.fields.Object
