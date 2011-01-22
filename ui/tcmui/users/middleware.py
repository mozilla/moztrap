from ..core.api import Credentials

class AuthenticationMiddleware(object):
    def process_request(self, request):
        # @@@ persisting plaintext pw in session
        user = request.session.get("user")
        password = request.session.get("password")
        if user and password:
            request.auth = Credentials(user, password)
        else:
            request.auth = None
