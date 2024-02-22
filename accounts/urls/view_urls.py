from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from accounts.views import (
    IndexView,
    RegisterView,
    ActivateView,
    CustomLoginView,
    ResetPasswordView,
    ChangePasswordView,
    ProfileView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("signup/", RegisterView.as_view(), name="signup"),
    path("activate/<uidb64>/<token>/", ActivateView.as_view(), name="activate"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="logout.html"),
        name="logout",
    ),
    path("password-reset/", ResetPasswordView.as_view(), name="password-reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html",
            success_url=reverse_lazy("password-reset-complete"),
        ),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password-reset-complete",
    ),
    path("password-change/", ChangePasswordView.as_view(), name="password-change"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
