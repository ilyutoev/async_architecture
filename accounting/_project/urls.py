from django.contrib import admin
from django.urls import include
from django.urls import path

urlpatterns = [
    path('analytics/', include('analytics.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('authn.urls')),
    path('', include('accounting.urls')),
]
