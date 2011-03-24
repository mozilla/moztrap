class EnumMetaclass(type):
    def __new__(cls, name, bases, attrs):
        base_attrs = {}
        for base in bases:
            base_attrs.update(getattr(base, "_forward_map", {}))
        base_attrs.update(attrs)
        _forward_map = {}
        _reverse_map = {}
        for k, v in base_attrs.iteritems():
            if v in _reverse_map:
                raise ValueError(
                    "Enum %s has duplicate attributes with value %r."
                    % (name, v))
            _forward_map[k] = v
            _reverse_map[v] = k
        return super(EnumMetaclass, cls).__new__(
            cls, name, bases, {"_forward_map": _forward_map,
                               "_reverse_map": _reverse_map})


    def __getattr__(cls, k):
        return cls._forward_map[k]


    def __getitem__(cls, k):
        return cls._reverse_map[k]



class Enum(object):
    __metaclass__ = EnumMetaclass

