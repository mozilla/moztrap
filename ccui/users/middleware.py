from .util import get_user



def get_user_from_request(request):
    userid = request.session.get("userid")
    cookie = request.session.get("cookie")

    user = None
    if userid and cookie:
        user = get_user(userid, cookie=cookie)
        if not user:
            request.session.flush()
    return user



class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            request._cached_user = get_user_from_request(request)
        return request._cached_user



class LazyAuth(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_auth'):
            request._cached_auth = None
            if request.user:
                request._cached_auth = request.user.auth
        return request._cached_auth



class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.__class__.user = LazyUser()
        request.__class__.auth = LazyAuth()
