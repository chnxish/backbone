from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

from utils.validate import validate_username, validate_password

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": _("Email is required."),
            "blank": _("Email cannot be blank."),
        },
    )
    username = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            "required": _("Username is required."),
            "blank": _("Username cannot be blank."),
        },
    )
    password = serializers.CharField(
        max_length=50,
        required=True,
        error_messages={
            "required": _("Password is required."),
            "blank": _("Password cannot be blank."),
        },
    )
    confirm_password = serializers.CharField(
        max_length=50,
        required=True,
        error_messages={
            "required": _("Confirm password is required."),
            "blank": _("Confirm password cannot be blank."),
        },
    )

    def validate(self, attrs):
        email = attrs.get("email")
        username = attrs.get("username")
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        try:
            user_email = User.objects.get(email=email)
        except User.DoesNotExist:
            user_email = None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user_email:
            raise serializers.ValidationError(
                _("Email ID already belongs to an account.")
            )
        if user:
            raise serializers.ValidationError(
                _("User with given username already exists.")
            )
        if not validate_username(username):
            raise serializers.ValidationError(_("Not a valid username."))
        if not password or not confirm_password:
            raise serializers.ValidationError(_("Please provide all details."))
        if not validate_password(password):
            raise serializers.ValidationError(
                _(
                    "Password must contain 1 number, 1 upper-case and lower-case letter,"
                    " and must be at least 8 characters long."
                )
            )
        if password == email:
            raise serializers.ValidationError(_("Password cannot be your Email ID."))
        if password != confirm_password:
            raise serializers.ValidationError(_("Password fields did not match."))

        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": _("Email is required."),
            "blank": _("Email cannot be blank."),
        },
    )
    password = serializers.CharField(
        max_length=50,
        required=True,
        error_messages={
            "required": _("Password is required."),
            "blank": _("Password cannot be blank."),
        },
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if not user:
            raise serializers.ValidationError(
                _("Account with email does not exists."),
                code=status.HTTP_404_NOT_FOUND,
            )
        if not user.check_password(password):
            raise serializers.ValidationError(
                _("Password is incorrect."),
                code=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            raise serializers.ValidationError(_("User is not active."))

        return attrs
