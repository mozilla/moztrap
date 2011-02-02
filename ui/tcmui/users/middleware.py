from .util import get_user, logout



def get_user_from_request(request):
    # @@@ should not be persisting plaintext pw in session, but
    #     currently API doesn't allow any other technique
    userid = request.session.get("userid")
    password = request.session.get("password")

    user = None
    if userid and password:
        user = get_user(userid, password)
        if not user:
            logout(request)
    return user



class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            request._cached_user = get_user_from_request(request)
        return request._cached_user



class LazyAuth(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_auth'):
            request._cached_auth=None
            if request.user:
                request._cached_auth = request.user.auth
        return request._cached_auth



class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.__class__.user = LazyUser()
        request.__class__.auth = LazyAuth()
