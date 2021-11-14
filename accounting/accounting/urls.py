from django.urls import path

from accounting.views import index

urlpatterns = [
    path('', index, name='index')
]
