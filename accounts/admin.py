from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from accounts.forms import RegisterForm, UpdateUserForm
from accounts.models import Profile

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = RegisterForm
    form = UpdateUserForm
    model = User
    list_display = ("username", "email", "is_staff", "is_active")
    list_filter = ("email", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ("user", "bio")
    list_filter = ("user",)
    fieldsets = ((None, {"fields": ("avatar", "bio")}),)

    def has_add_permission(self, request):
        return False


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
