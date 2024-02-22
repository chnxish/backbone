from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from accounts.models import Profile
from utils.validate import validate_password, validate_username

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control",
            }
        ),
        error_messages={
            "required": _("Email is required."),
            "blank": _("Email cannot be blank."),
        },
    )
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control",
            }
        ),
        error_messages={
            "required": _("Username is required."),
            "blank": _("Username cannot be blank."),
        },
    )
    password1 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control",
                "data-toggle": "password",
                "id": "password",
            }
        ),
        error_messages={
            "required": _("Password is required."),
            "blank": _("Password cannot be blank."),
        },
    )
    password2 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": "form-control",
                "data-toggle": "password",
                "id": "password",
            }
        ),
        error_messages={
            "required": _("Confirm password is required."),
            "blank": _("Confirm password cannot be blank."),
        },
    )

    def clean(self):
        email = self.cleaned_data.get("email")
        username = self.cleaned_data.get("username")
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        try:
            user_email = User.objects.get(email=email)
        except User.DoesNotExist:
            user_email = None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user_email:
            raise forms.ValidationError(_("Email ID already belongs to an account."))
        if user:
            raise forms.ValidationError(_("User with given username already exists."))
        if not validate_username(username):
            raise forms.ValidationError(_("Not a valid username."))
        if not password1 or not password2:
            raise forms.ValidationError(_("Please provide all details."))
        if not validate_password(password1):
            raise forms.ValidationError(
                _(
                    "Password must contain 1 number, 1 upper-case and lower-case letter,"
                    " and must be at least 8 characters long."
                )
            )
        if password1 == email:
            raise forms.ValidationError(_("Password cannot be your Email ID."))
        if password1 != password2:
            raise forms.ValidationError(_("Password fields did not match."))

        return self.cleaned_data

    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control",
            }
        ),
        error_messages={
            "required": _("Email is required."),
            "blank": _("Email cannot be blank."),
        },
    )
    password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control",
                "data-toggle": "password",
                "id": "password",
                "name": "password",
            }
        ),
        error_messages={
            "required": _("Password is required."),
            "blank": _("Password cannot be blank."),
        },
    )
    remember_me = forms.BooleanField(required=False)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if not user:
            raise forms.ValidationError(
                _("Account with email does not exists."),
            )
        if not user.check_password(password):
            raise forms.ValidationError(
                _("Password is incorrect."),
            )
        if not user.is_active:
            raise forms.ValidationError(_("User is not active."))

        self.user_cache = authenticate(self.request, email=email, password=password)

        return self.cleaned_data

    def get_user(self):
        return self.user_cache

    class Meta:
        model = User
        fields = ["email", "password", "remember_me"]


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
        error_messages={
            "required": _("Username is required."),
            "blank": _("Username cannot be blank."),
        },
    )

    class Meta:
        model = User
        fields = ["username"]


class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control-file"})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5})
    )

    class Meta:
        model = Profile
        fields = ["avatar", "bio"]
