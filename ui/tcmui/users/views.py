from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..core.api import admin

from . import util
from .forms import LoginForm, RegistrationForm
from .models import UserList, User



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
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data["company"] = request.company
            user = User(**data)
            UserList.get(auth=admin).post(user)
            # @@@ user.setroles(...)

            # @@@ Email confirmation step missing.
            messages.success(
                request,
                "Congratulations, you've registered! Now you can login."
                )
            return redirect("home")
    else:
        form = RegistrationForm()

    return TemplateResponse(request, "account/register.html", {"form": form})
