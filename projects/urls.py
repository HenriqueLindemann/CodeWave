from django.urls import path
from . import views

app_name = 'projects'  

urlpatterns = [
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('create-project/', views.create_project, name='create_project'),
    path('search_projects/', views.search_projects, name='search_projects'),
    path('results_search_projects/', views.results_search_projects, name='results_search_projects'),
    path('search_tasks/', views.search_tasks, name='search_tasks'),
    path('results_search_tasks/', views.results_search_tasks, name='results_search_tasks'),

    path('edit/<int:project_id>/', views.edit_project, name='edit_project'),

    path('task/<int:task_id>/apply/', views.apply_for_task, name='apply_for_task'),
    path('application/<int:application_id>/review/', views.review_application, name='review_application'),

]
