# coding=utf-8

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Skill
from .forms import UserAdminCreationForm, UserAdminForm

class UserAdmin(BaseUserAdmin):
    add_form = UserAdminCreationForm
    form = UserAdminForm
    model = User
    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password1', 'password2', 'is_developer', 'is_client'),
            'classes': ('wide',)
        }),
    )
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('name', 'balance', 'rank', 'rating', 'skills', 'bio')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login',),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
    list_display = ['username', 'name', 'email', 'is_active', 'is_staff', 'date_joined']
    search_fields = ('username', 'name', 'email')
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined','password')  # Set date_joined as readonly

admin.site.register(User, UserAdmin)

class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Exibe o nome e a descrição na lista de habilidades
    search_fields = ('name',)  # Permite buscar habilidades pelo nome
    ordering = ('name',)  # Ordena as habilidades alfabeticamente pelo nome

admin.site.register(Skill, SkillAdmin)