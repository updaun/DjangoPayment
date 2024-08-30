from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from accounts.models import User
from accounts.forms import SignupForm, LoginForm


signup = CreateView.as_view(
    model=User,
    form_class=SignupForm,
    template_name="accounts/signup_form.html",
    success_url=reverse_lazy("login"),
)


login = LoginView.as_view(
    form_class=LoginForm,
    template_name="accounts/login_form.html",
)


def logout(request):
    pass


def profile(request):
    pass
