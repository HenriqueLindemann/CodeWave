from django.urls import path
from .views import edit_profile

urlpatterns = [
    path('edit-profile/', edit_profile, name='edit_profile'),
]