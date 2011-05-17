from .responses import make_array, make_one, make_list, make_searchresult



class SingleBuilder(object):
    def __init__(self, name, defaults=None,
                 add_identity=True, add_timeline=True):
        self.name = name
        self.defaults = defaults
        self.add_identity = add_identity
        self.add_timeline = add_timeline


    def one(self, **kwargs):
        kwargs.setdefault("add_identity", self.add_identity)
        kwargs.setdefault("add_timeline", self.add_timeline)
        return {
            "ns1.%s" % self.name: [
                make_one(
                    self.name,
                    defaults=self.defaults,
                    **kwargs)
                ]
            }



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


    def _list(self, *dicts):
        return make_list(
            self.name,
            self.plural_name,
            *dicts,
            defaults=self.defaults,
            add_identity=self.add_identity,
            add_timeline=self.add_timeline)
