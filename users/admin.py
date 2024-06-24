from django.contrib import admin
from .models import UserProfile, Skill, Tag

class SkillInline(admin.TabularInline):
    model = UserProfile.skills.through
    extra = 1

class TagInline(admin.TabularInline):
    model = UserProfile.tags.through
    extra = 1

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    inlines = [SkillInline, TagInline]
    list_display = ['user', 'bio', 'phone_number']
    exclude = ('skills', 'tags',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
