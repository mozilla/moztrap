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
