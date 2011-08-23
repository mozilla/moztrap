from django.conf import settings
from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..core.conf import conf
from ..core.auth import admin

from . import util
from .forms import LoginForm, RegistrationForm
from .models import RoleList



def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            util.login(request, form.user)

            to = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
            if " " in to or "//" in to:
                raise SuspiciousOperation(
                    "Redirect should not have spaces or be absolute.")

            return redirect(to)
    else:
        form = LoginForm()

    return TemplateResponse(request, "account/login.html", {"form": form})



def logout(request):
    util.logout(request)
    messages.success(request, "You're logged out - see you next time!")
    return redirect("login")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, company=request.company)
        if form.is_valid():
            user = form.user
            user.roles = RoleList(
                entries=[conf.TCM_NEW_USER_ROLE_ID], auth=admin)
            # @@@ Email confirmation step missing.
            user.activate(auth=admin)
            messages.success(
                request,
                "Congratulations, you've registered! Now you can login."
                )
            return redirect("login")
    else:
        form = RegistrationForm(company=request.company)

    return TemplateResponse(request, "account/register.html", {"form": form})
