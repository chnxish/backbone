from django.contrib import admin

from friendship.models import FriendshipRequest, Friend


class FriendshipRequestAdmin(admin.ModelAdmin):
    model = FriendshipRequest
    list_display = ("from_user", "to_user")
    list_filter = ("from_user", "to_user")
    fieldsets = (
        (None, {"fields": ("from_user", "to_user", "content", "created")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "from_user",
                    "to_user",
                    "content",
                )
            }
        )
    )


class FriendAdmin(admin.ModelAdmin):
    model = Friend
    list_display = ("from_user", "to_user")
    list_filter = ("from_user", "to_user")
    fieldsets = (
        (None, {"fields": ("from_user", "to_user", "created")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "from_user",
                    "to_user",
                )
            }
        )
    )


admin.site.register(FriendshipRequest, FriendshipRequestAdmin)
admin.site.register(Friend, FriendAdmin)
