from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/<str:task_id>/", views.task_detail, name="task_detail"),
]
