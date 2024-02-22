from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views import View
from rest_framework import status, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.forms import LoginForm, RegisterForm, UpdateUserForm, UpdateProfileForm
from accounts.serializers import RegisterSerializer, LoginSerializer
from accounts.tokens import generate_token
from backbone import settings
from utils.handle_error_message import get_first_error

User = get_user_model()


class RegisterViewMixin:
    def create_and_send_activation_email(
        self, email, username, password, protocol, domain
    ):
        user = User.objects.create(
            email=email,
            username=username,
        )
        user.set_password(password)
        user.is_active = False
        user.save()

        # Email Address Confirmation Email
        subject = "[Backbone] Confirm your Email"
        message = render_to_string(
            "activate_email.html",
            {
                "protocol": protocol,
                "domain": domain,
                "uid": urlsafe_base64_encode(force_bytes(user.id)),
                "token": generate_token.make_token(user),
            },
        )
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        return user


class ExceptionHandlerMixin:
    def handle_exception(self, exc):
        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            response_data = {
                "status": False,
                "message": _("You do not have permission to perform this action."),
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

        return super().handle_exception(exc)


class RegisterAPIView(RegisterViewMixin, APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            self.create_and_send_activation_email(
                serializer.validated_data.get("email"),
                serializer.validated_data.get("username"),
                serializer.validated_data.get("password"),
                request.scheme,
                get_current_site(request).domain,
            )

            response_content = {
                "status": True,
                "message": _(
                    "Your account has been created successfully! Please check your email"
                    " to confirm your email address in order to activate your account."
                ),
            }
            return Response(response_content, status=status.HTTP_201_CREATED)
        else:
            response_content = {
                "status": False,
                "message": get_first_error(serializer.errors),
            }
            return Response(response_content, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            user = User.objects.get(email=email)
            token, created = Token.objects.get_or_create(user=user)
            content = {
                "token": token.key,
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "avatar": request.build_absolute_uri(user.user_profile.avatar.url),
            }

            response_content = {
                "status": True,
                "message": _("User logged in successfully."),
                "data": content,
            }
            return Response(response_content, status=status.HTTP_200_OK)
        else:
            response_content = {
                "status": False,
                "message": get_first_error(serializer.errors),
            }
            return Response(response_content, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView, ExceptionHandlerMixin):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        token = Token.objects.get(user=user)
        token.delete()

        response_content = {
            "status": True,
            "message": _("User logged out successfully."),
        }
        return Response(response_content, status=status.HTTP_202_ACCEPTED)


class IndexView(View):
    def get(self, request):
        return render(request, "home.html")


class RegisterView(RegisterViewMixin, View):
    form_class = RegisterForm
    initial = {"key": "value"}
    template_name = "register.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")

        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            self.create_and_send_activation_email(
                form.cleaned_data.get("email"),
                form.cleaned_data.get("username"),
                form.cleaned_data.get("password1"),
                request.scheme,
                get_current_site(request).domain,
            )

            messages.success(
                request,
                "Your account has been created successfully! Please check your email"
                " to confirm your email address in order to activate your account.",
            )
            return redirect("login")

        return render(request, self.template_name, {"form": form})


class ActivateView(View):
    failed_template_name = "activate_failed.html"

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated!")
            return redirect("login")
        else:
            return render(request, self.failed_template_name)


class CustomLoginView(LoginView):
    form_class = LoginForm
    authentication_form = LoginForm
    template_name = "login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data.get("remember_me")

        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True

        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "password_reset.html"
    from_email = settings.EMAIL_HOST_USER
    email_template_name = "password_reset_email.html"
    subject_template_name = "password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("home")


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = "change_password.html"
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy("home")


class ProfileView(View):
    template_name = "profile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super(ProfileView, self).dispatch(request, *args, **kwargs)

        return redirect("/")

    def get(self, request):
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.user_profile)
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )

    def post(self, request):
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.user_profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile is updated successfully")
            return redirect("profile")

        return render(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )
