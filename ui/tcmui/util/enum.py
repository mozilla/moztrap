class EnumMetaclass(type):
    def __new__(cls, name, bases, attrs):
        base_attrs = {}
        for base in bases:
            base_attrs.update(getattr(base, "_forward_map", {}))
        base_attrs.update(attrs)
        _forward_map = {}
        _reverse_map = {}
        new_attrs = {}
        for k, v in base_attrs.iteritems():
            if k.startswith("_"):
                new_attrs[k] = v
                continue
            if v in _reverse_map:
                raise ValueError(
                    "Enum %s has duplicate attributes with value %r."
                    % (name, v))
            _forward_map[k] = v
            _reverse_map[v] = k
        new_attrs["_forward_map"] = _forward_map
        new_attrs["_reverse_map"] = _reverse_map
        return super(EnumMetaclass, cls).__new__(cls, name, bases, new_attrs)


    def __getattr__(cls, k):
        try:
            return cls._forward_map[k]
        except KeyError:
            try:
                return cls.__dict__[k]
            except KeyError:
                raise AttributeError(
                    "%r object has no attribute %r" % (cls.__name__, k))



    def __getitem__(cls, k):
        return cls._reverse_map[k]



class Enum(object):
    __metaclass__ = EnumMetaclass

