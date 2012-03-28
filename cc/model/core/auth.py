"""
Proxy User and Role models.

"""
from django.contrib.auth.backends import ModelBackend as DjangoModelBackend
# Permission is imported solely so other places can import it from here
from django.contrib.auth.models import User as BaseUser, Group, Permission

from registration.models import RegistrationProfile


# monkeypatch the User model to ensure unique email addresses
BaseUser._meta.get_field("email")._unique = True


class User(BaseUser):
    """Proxy for contrib.auth User that adds action methods and roles alias."""
    class Meta:
        proxy = True


    def delete(self, user=None):
        """
        Delete this user.

        We ignore the passed-in user since User is not a CCModel and doesn't
        track created_by / modified_by.

        We have to delete registration profiles manually, to avoid
        https://code.djangoproject.com/ticket/16128.

        """
        # @@@ Django ticket 16128, hopefully fixed in 1.4?
        # RegistrationProfile's FK is to Django's user model, not ours
        RegistrationProfile.objects.filter(user=self).delete()
        super(User, self).delete()


    def activate(self, user=None):
        """Activate this user."""
        self.is_active = True
        self.save(force_update=True)


    def deactivate(self, user=None):
        """Deactivate this user."""
        self.is_active = False
        self.save(force_update=True)


    @property
    def roles(self):
        """Maps our name (roles) to Django name (groups)."""
        return self.groups



Role = Group



class ModelBackend(DjangoModelBackend):
    """Authentication backend that returns instances of our proxy User model."""
    def authenticate(self, username=None, password=None):
        """Return User for given credentials, or None."""
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None


    def get_user(self, user_id):
        """Return User for given ID, or None."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
