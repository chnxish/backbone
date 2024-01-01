from datetime import datetime, timedelta

from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.shortcuts import get_object_or_404

from .models import CustomUser
from .serializers import CustomUserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = "username"

    def validate(self, attrs):
        current_time = datetime.now()

        data = super().validate(attrs)
        data["access_expires_in"] = current_time + timedelta(minutes=30)
        data["refresh_expires_in"] = current_time + timedelta(days=1)
        data["id"] = self.user.id
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["access_expires_in"] = datetime.now() + timedelta(minutes=30)
        return data


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    def get_queryset(self):
        # return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)

    def create(self, request):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        if str(request.user.id) != str(pk):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(self.get_queryset(), pk=pk)
        data = request.data.copy()
        serializer = self.get_serializer(user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        if str(request.user.id) != str(pk):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        if str(request.user.id) != str(pk):
            return Response(
                {"detail": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(self.get_queryset(), pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
