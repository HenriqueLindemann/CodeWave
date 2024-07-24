from django.urls import path
from . import views

app_name = 'projects'  

urlpatterns = [
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('create-project/', views.create_project, name='create_project'),

]
