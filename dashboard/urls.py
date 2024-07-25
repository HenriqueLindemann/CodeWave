from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.utils.decorators import method_decorator
from . import views
from .views import change_language
from django.conf.urls.i18n import i18n_patterns

app_name = 'dashboard'

urlpatterns = [
    path("", views.index, name="index"),
    path('change_language/<str:language_code>/', change_language, name='change_language'),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('projects/', include(('projects.urls', 'projects'), namespace='projects')),


] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
