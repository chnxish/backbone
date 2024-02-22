from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

from friendship.models import FriendshipRequest

User = get_user_model()


class SendFriendRequestSerializer(serializers.Serializer):
    from_username = serializers.CharField(error_messages={
        "required": _("From username is required."),
        "blank": _("From username cannot be blank."),
    })
    to_username = serializers.CharField(error_messages={
        "required": _("To username is required."),
        "blank": _("To username cannot be blank."),
    })

    def validate(self, attrs):
        from_username = attrs.get("from_username")
        to_username = attrs.get("to_username")

        try:
            from_user = User.objects.get(username=from_username)
        except User.DoesNotExist:
            from_user = None

        try:
            to_user = User.objects.get(username=to_username)
        except User.DoesNotExist:
            to_user = None

        if not from_user or not to_user:
            raise serializers.ValidationError(
                _("User(s) account does not exist."),
                code=status.HTTP_404_NOT_FOUND,
            )

        friendship_request = FriendshipRequest.objects.filter(
            from_user=from_user, to_user=to_user
        )

        for request in friendship_request:
            if request.is_active:
                raise serializers.ValidationError(
                    _("Friend request already sent to the user."),
                    code=status.HTTP_409_CONFLICT,
                )

        return attrs
