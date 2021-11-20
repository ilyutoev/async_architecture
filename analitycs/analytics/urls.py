from django.urls import path

from analytics.views import index

urlpatterns = [
    path('', index, name='analytics_index')
]
