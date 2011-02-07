from .models import EnvironmentList, Environment


def get_envs_from_request(request):
    envs = request.session.get("environments", [])

    return EnvironmentList(entries=
        [Environment.get("environments/%s" % eid, auth=request.auth)
         for etid, eid in envs])



class LazyEnvironments(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_envs'):
            request._cached_envs = get_envs_from_request(request)
        return request._cached_envs



class EnvironmentsMiddleware(object):
    def process_request(self, request):
        request.__class__.environments = LazyEnvironments()
