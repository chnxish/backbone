from django.urls import path

from accounts.views import RegisterAPIView, LoginAPIView, LogoutAPIView

urlpatterns = [
    path("signup/", RegisterAPIView.as_view(), name="signup"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
