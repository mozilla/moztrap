"""
Account-related forms.

"""
import operator
import random

from django.conf import settings

from django.contrib.auth import forms as auth_forms

import floppyforms as forms
from registration import forms as registration_forms

from cc import model



def check_password(pw):
    """
    Enforce password strength rules.

    Returns the password if it passes, otherwises raises ``ValidationError``.

    """
    if len(pw) < settings.MINIMUM_PASSWORD_CHARS:
        raise forms.ValidationError(
            "Your password must be a minimum of {0} characters.".format(
                settings.MINIMUM_PASSWORD_CHARS)
            )
    if (settings.PASSWORD_REQUIRE_ALPHA_NUMERIC and
        not (any(c.isdigit() for c in pw) and any(c.isalpha() for c in pw))
        ):
        raise forms.ValidationError(
            "Your password must contain both letters and numbers.")
    if pw in settings.FORBIDDEN_PASSWORDS:
        raise forms.ValidationError(
            "That password is too easily guessed; please choose a different one.")
    return pw


class SetPasswordFormMixin(object):
    """
    Mixin class for password-changing forms.

    Enforces password strength rules, sets label for password confirmation
    field.

    """
    def __init__(self, *args, **kwargs):
        """After form initialization, change label for new_password2 field."""
        super(SetPasswordFormMixin, self).__init__(*args, **kwargs)

        self.fields["new_password2"].label = "New password (again)"


    def clean_new_password1(self):
        """Enforce minimum password strength rules."""
        return check_password(self.cleaned_data["new_password1"])



class SetPasswordForm(SetPasswordFormMixin, auth_forms.SetPasswordForm):
    pass



class ChangePasswordForm(SetPasswordFormMixin, auth_forms.PasswordChangeForm):
    pass



class RegistrationForm(registration_forms.RegistrationForm):
    """A registration form that enforces our password rules."""
    def clean_password1(self):
        """Enforce minimum password strength rules."""
        return check_password(self.cleaned_data["password1"])


    def clean_email(self):
        """
        Validate that the email is not already in use.

        """
        try:
            model.User.objects.get(email=self.cleaned_data["email"])
        except model.User.DoesNotExist:
            return self.cleaned_data["email"]
        raise forms.ValidationError(u"A user with that email already exists.")



class PasswordResetForm(auth_forms.PasswordResetForm):
    """A password reset form that doesn't reveal valid users."""
    def clean_email(self):
        """No validation that the email address exists."""
        return self.cleaned_data["email"]


    def save(self, *args, **kwargs):
        """Fetch the affected users here before sending reset emails."""
        email = self.cleaned_data["email"]
        # super's save expects self.users_cache to be set.
        self.users_cache = model.User.objects.filter(
            email__iexact=email, is_active=True)

        return super(PasswordResetForm, self).save(*args, **kwargs)




OPERATORS = {
    "plus": operator.add,
    "minus": operator.sub,
    "times": operator.mul,
    }

CAPTCHA_SESSION_KEY = "auth_captcha_answer"



class CaptchaAuthenticationForm(auth_forms.AuthenticationForm):
    """
    Login form with a simple math captcha.

    For use when there have been too many failed login attempts from a
    particular IP address or for a particular username. Simply locking users
    out in this case creates a potential Denial of Service vulnerability; a
    captcha allows a human to still log in but makes life more difficult for
    the brute-force attacker.

    Expected answer to captcha is stored in the session; this avoids replay
    attacks and the need to trust client input, at the cost of somewhat higher
    likelihood of spurious failure, e.g. if the user opens up captcha login
    forms in two tabs and then tries to use the first one.

    """
    def __init__(self, *args, **kwargs):
        """Initialize form, including captcha question and expected answer."""
        super(CaptchaAuthenticationForm, self).__init__(*args, **kwargs)

        # get previous expected answer before generating new one
        self.captcha_answer = self.request.session.get(CAPTCHA_SESSION_KEY)

        # only add the captcha field if this request hit the rate limit
        if getattr(self.request, "limited", False):
            a, b = random.randint(1,9), random.randint(1, 9)
            # avoid negative answers
            if b > a:
                a, b = b, a
            opname, op = random.choice(OPERATORS.items())

            # store the expected answer in the session
            self.request.session[CAPTCHA_SESSION_KEY] = op(a, b)

            self.fields["captcha"] = forms.IntegerField(
                widget=forms.TextInput,
                required=False,
                label=u"What is {0} {1} {2}?".format(a, opname, b),
                )


    def clean_captcha(self):
        """
        Fail form validation if captcha answer is not the expected answer.

        If no expected captcha answer was previously generated (this is the
        request on which they hit the rate limit for the first time) and no
        captcha answer was provided in the POST data, we don't fail them -- if
        they've got the right username and password on the login attempt that
        first hits the rate limit, their login should succeed.

        """
        answer = self.cleaned_data.get("captcha")
        if answer != self.captcha_answer:
            raise forms.ValidationError(
                "Sorry, that's not the answer we were looking for.")
