from .responses import (
    make_array, make_one, make_identity, make_searchresult, make_timeline,
    make_list)



class SingleBuilder(object):
    def __init__(self, name, defaults=None,
                 add_identity=True, add_timeline=True):
        self.name = name
        self.defaults = defaults or {}
        self.add_identity = add_identity
        self.add_timeline = add_timeline


    def one(self, **kwargs):
        return {
            "ns1.%s" % self.name: [
                self._one(**kwargs)
                ]
            }


    def _one(self, **kwargs):
        data = self.defaults.copy()
        data.update(kwargs)

        if self.add_identity:
            identity_data = {}
            for name in ["_id", "_url", "_version"]:
                if name in data:
                    identity_data[name.lstrip("_")] = data.pop(name)

            data.setdefault(
                "resourceIdentity", make_identity(**identity_data))

        if self.add_timeline:
            data.setdefault("timeline", make_timeline())

        return make_one(self.name, **data)



class ListBuilder(SingleBuilder):
    def __init__(self, name, plural_name, array_name,
                 defaults=None, add_identity=True, add_timeline=True):
        self.plural_name = plural_name
        self.array_name = array_name
        super(ListBuilder, self).__init__(name, defaults,
                                          add_identity, add_timeline)


    def searchresult(self, *dicts):
        return make_searchresult(
            self.name,
            self.plural_name,
            *self._list(*dicts)
            )


    def array(self, *dicts):
        return make_array(
            self.name,
            self.array_name,
            *self._list(*dicts))


    def list(self, *dicts):
        return make_list(
            self.name,
            *self._list(*dicts))


    def _one(self, **kwargs):
        if self.add_identity and "_id" in kwargs and "_url" not in kwargs:
            kwargs["_url"] = "%s/%s" % (self.plural_name, kwargs["_id"])
        return super(ListBuilder, self)._one(**kwargs)


    def _list(self, *dicts):
        ret = []
        for i, info in enumerate(dicts):
            if self.add_identity:
                info.setdefault("_id", i+1)
            ret.append(self._one(**info))
        return ret
