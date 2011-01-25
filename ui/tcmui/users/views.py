from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..core.api import admin

from .forms import RegistrationForm
from .models import UserList, User



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
