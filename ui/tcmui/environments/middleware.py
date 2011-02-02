from .models import EnvironmentGroup


def get_env_from_request(request):
    env_group_id = request.session.get("environment_group_id", None)

    env_group = None
    if env_group_id:
        env_group = EnvironmentGroup.get(
            "environmentgroups/%s" % env_group_id,
            auth=request.auth)
    return env_group



class LazyEnvironmentGroup(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_env'):
            request._cached_env = get_env_from_request(request)
        return request._cached_env



class EnvironmentMiddleware(object):
    def process_request(self, request):
        request.__class__.environmentgroup = LazyEnvironmentGroup()
