# coding=utf-8

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'accounts' 

urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('search_developer/', views.search_developer, name='search_developer'),
    path('results_search_devs/', views.results_search_devs, name='results_search_devs'),
]