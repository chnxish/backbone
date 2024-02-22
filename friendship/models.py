from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from friendship.exceptions import AlreadyFriendsError, AlreadyExistsError

User = get_user_model()


class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendship_request_sender"
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendship_request_receiver"
    )
    content = models.TextField(_("content"), blank=True)
    created = models.DateTimeField(_("created"), default=timezone.now)
    rejected = models.DateTimeField(_("rejected"), blank=True, null=True)
    viewed = models.DateTimeField(_("viewed"), blank=True, null=True)

    class Meta:
        verbose_name = _("friendship request")
        verbose_name_plural = _("friendship request")
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"User {self.from_user_id} friendship requested {self.to_user_id}"

    def accept(self):
        Friend.objects.create(from_user=self.from_user, to_user=self.to_user)
        Friend.objects.create(from_user=self.to_user, to_user=self.from_user)

        self.delete()

        FriendshipRequest.objects.filter(
            from_user=self.to_user, to_user=self.from_user
        ).delete()

        return True

    def reject(self):
        self.rejected = timezone.now()
        self.save()
        return True

    def cancel(self):
        self.delete()
        return True

    def mark_viewed(self):
        self.viewed = timezone.now()
        self.save()
        return True


class FriendshipManager(models.Manager):
    def friends(self, user):
        qs = Friend.objects.select_related("from_user").filter(to_user=user)
        friends = [u.from_user for u in qs]
        return friends

    def requests(self, user):
        qs = FriendshipRequest.objects.filter(to_user=user)
        qs = self._friendship_request_select_related(qs, "from_user", "to_user")
        requests = list(qs)
        return requests

    def sent_requests(self, user):
        qs = FriendshipRequest.objects.filter(from_user=user)
        qs = self._friendship_request_select_related(qs, "from_user", "to_user")
        requests = list(qs)
        return requests

    def has_unread_requests(self, user):
        return FriendshipRequest.objects.filter(to_user=user, viewed__isnull=True).exists()

    def add_friend(self, from_user, to_user, message=""):
        if from_user == to_user:
            raise ValidationError(_("Users cannot be friends with themselves."))

        if self.are_friends(from_user, to_user):
            raise AlreadyFriendsError(_("Users are already friends."))

        if FriendshipRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).exists():
            raise AlreadyExistsError(_("You already requested friendship from this user."))

        if FriendshipRequest.objects.filter(
            from_user=to_user, to_user=from_user
        ).exists():
            raise AlreadyExistsError(_("This user already requested friendship from you."))

        request, created = FriendshipRequest.objects.get_or_create(
            from_user=from_user, to_user=to_user
        )

        if created is False:
            raise AlreadyExistsError(_("Friendship already requested."))

        request.message = message
        request.save()
        return request

    def remove_friend(self, from_user, to_user):
        qs = Friend.objects.filter(
            to_user__in=[to_user, from_user],
            from_user__in=[from_user, to_user],
        )

        if qs:
            qs.delete()
            return True
        else:
            return False

    def are_friends(self, user1, user2):
        try:
            Friend.objects.get(to_user=user1, from_user=user2)
            return True
        except Friend.DoesNotExist:
            return False

    def _friendship_request_select_related(self, qs, *fields):
        strategy = getattr(
            settings,
            "FRIENDSHIP_MANAGER_FRIENDSHIP_REQUEST_SELECT_RELATED_STRATEGY",
            "select_related",
        )
        if strategy == "select_related":
            qs = qs.select_related(*fields)
        elif strategy == "prefetch_related":
            qs = qs.prefetch_related(*fields)
        return qs


class Friend(models.Model):
    from_user = models.ForeignKey(User, models.CASCADE, related_name="_unused_friend_relation")
    to_user = models.ForeignKey(User, models.CASCADE, related_name="friends")
    created = models.DateTimeField(default=timezone.now)

    objects = FriendshipManager()

    class Meta:
        verbose_name = _("friend")
        verbose_name_plural = _("friend")
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"User {self.to_user_id} is friends with {self.from_user_id}"

    def save(self, *args, **kwargs):
        if self.to_user == self.from_user:
            raise ValidationError(_("Users cannot be friends with themselves."))
        super().save(*args, **kwargs)
