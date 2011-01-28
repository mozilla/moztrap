from .util import get_user, logout


class AuthenticationMiddleware(object):
    def process_request(self, request):
        # @@@ should not be persisting plaintext pw in session, but
        #     currently API doesn't allow any other technique
        userid = request.session.get("userid")
        password = request.session.get("password")

        request.auth = None
        request.user = None
        if userid and password:
            user = get_user(userid, password)
            if user:
                request.user = user
                request.auth = user.auth
            else:
                logout(request)
