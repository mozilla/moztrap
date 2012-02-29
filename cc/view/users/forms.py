# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Account-related forms.

"""
import operator
import random

from django.contrib.auth import forms as auth_forms

import floppyforms as forms



class UpdateLabelMixin(object):
    """Mixin class to change confirmation pw field label on auth forms."""
    def __init__(self, *args, **kwargs):
        """After form initialization, change label for new_password2 field."""
        super(UpdateLabelMixin, self).__init__(*args, **kwargs)

        self.fields["new_password2"].label = "New password (again)"



class SetPasswordForm(UpdateLabelMixin, auth_forms.SetPasswordForm):
    pass



class ChangePasswordForm(UpdateLabelMixin, auth_forms.PasswordChangeForm):
    pass



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
