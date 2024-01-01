from django.urls import path, include
from rest_framework import routers

from .views import CustomTokenObtainPairView, CustomTokenRefreshView, CustomUserViewSet

router = routers.DefaultRouter()
router.register("users", CustomUserViewSet, basename="user")

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
