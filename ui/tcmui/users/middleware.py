from .util import get_user, logout


class AuthenticationMiddleware(object):
    def process_request(self, request):
        # @@@ persisting plaintext pw in session
        userid = request.session.get("userid")
        password = request.session.get("password")

        request.auth = None
        request.user = None
        if userid and password:
            user = get_user(userid, password)
            if user:
                request.user = user
            else:
                logout(request)
