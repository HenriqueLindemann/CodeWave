# coding=utf-8

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
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

    is_developer = models.BooleanField(_("Is Developer"), default=False)
    is_client = models.BooleanField(_("Is Client"), default=False)

    bio =models.TextField(_("Bio"),max_length=500,blank=True, null=True)

    balance = models.DecimalField(
        _("Balance"), 
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)], 
        help_text=_("Balance for future transaction implementation.")
    )
    rank = models.IntegerField(
        _("Rank"), 
        default=0, 
        validators=[MinValueValidator(0)], 
        help_text=_("User rank for future implementation.")
    )
    rating = models.DecimalField(
        _("Rating"), 
        max_digits=4, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(10)], 
        help_text=_("User rating, calculated as an average after each transaction.")
    )

    is_staff = models.BooleanField(_("Staff Status"), default=False)
    is_active = models.BooleanField(_("Active Status"), default=True)
    date_joined = models.DateTimeField(_("Date Joined"), auto_now_add=True)

    skills = models.ManyToManyField(
        'Skill', 
        related_name='users', 
        blank=True, 
        verbose_name=_("Skills")
    )

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

class Skill(models.Model):
    name = models.CharField(_("Skill Name"), max_length=100)
    description = models.TextField(_("Description"), null=True, blank=True)

    def __str__(self):
        return self.name
