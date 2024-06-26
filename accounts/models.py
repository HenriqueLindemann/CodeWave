# coding=utf-8

import re

from django.db import models
from django.core.validators import MaxLengthValidator, RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.core.validators import MaxLengthValidator, RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _("Username"), 
        max_length=30, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=_("Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."),
                code='invalid'
            )
        ],
        help_text=_("A username that will be used for identification and login on the platform."),
    )
    name = models.CharField(_("Name"), max_length=100, blank=True)
    email = models.EmailField(_("E-mail"), unique=True)
    is_staff = models.BooleanField(_("Staff Status"), default=False)
    is_active = models.BooleanField(_("Active Status"), default=True)
    date_joined = models.DateTimeField(_("Date Joined"), auto_now_add=True)
    institution = models.CharField(_("Institution"), max_length=100, blank=True)
    job = models.CharField(_("Job"), max_length=100, blank=True)
    role = models.CharField(_("Role"), max_length=100, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.name or self.username

    def get_short_name(self):
        return self.name.split(" ")[0] if self.name else self.username

    def user_has_role(self, role):
        return self.role == role

