from django.db import models
from django.conf import settings

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # Média das avaliações
    skills = models.ManyToManyField(Skill, blank=True)  # Relacionamento ManyToMany com Skill
    tags = models.ManyToManyField(Tag, blank=True)  # Relacionamento ManyToMany com Tag

    def __str__(self):
        return f'Profile of {self.user.username}'