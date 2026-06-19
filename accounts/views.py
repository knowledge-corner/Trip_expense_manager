from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("trips:home")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})
