from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from . import util
from .forms import LoginForm, RegistrationForm



def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            util.login(request, form.user)
            return redirect("products")
    else:
        form = LoginForm()

    return TemplateResponse(request, "home.html", {"form": form})



def logout(request):
    util.logout(request)
    messages.success(request, "You're logged out - see you next time!")
    return redirect("home")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, company=request.company)
        if form.is_valid():
            user = form.user
            # @@@ user.setroles(...)
            # @@@ activate
            # @@@ Email confirmation step missing.
            messages.success(
                request,
                "Congratulations, you've registered! Now you can login."
                )
            return redirect("home")
    else:
        form = RegistrationForm(company=request.company)

    return TemplateResponse(request, "account/register.html", {"form": form})
