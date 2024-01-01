import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


def user_avatar_path(instance, filename):
    ext = filename.split(".").pop()
    filename = "{0}.{1}".format(instance.username, ext)
    return os.path.join(filename)


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    avatar = models.ImageField(
        _("avatar"),
        upload_to=user_avatar_path,
        null=True,
        blank=True,
        default="/avatar/default_avatar.png",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = verbose_name
        ordering = ["-id"]
