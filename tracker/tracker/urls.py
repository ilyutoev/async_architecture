from django.urls import path

from tracker.views import index, add_task, done_task, assign_tasks

urlpatterns = [
    path('', index, name='index'),
    path('add/', add_task, name='add_task'),
    path('<int:pk>/done/', done_task, name='done_task'),
    path('assign_tasks/', assign_tasks, name='assign_tasks'),
]
