def by_type(environments):
    """
    Given an iterable of ``environments``, return a dictionary mapping
    environmentType IDs to a set of environment IDs of that type in the
    iterable.

    """
    types = {}
    for env in environments:
        et = env.environmentType
        options = types.setdefault(et.id, set())
        options.add(env.id)
    return types



def match(testenvs, matchenvs):
    """
    Return True if the given iterable of ``testenvs`` matches the given
    iterable of ``matchenvs``.

    If ``matchenvs`` includes multiple environments of the same type
    (e.g. Windows 7 and Windows Vista), it will match a set of environments
    containing either one of those.

    """
    types = by_type(testenvs)
    for type_id, envs in by_type(matchenvs).iteritems():
        try:
            if not types[type_id].issubset(envs):
                return False
        except KeyError:
            return False
    return True
