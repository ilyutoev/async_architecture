from django.contrib import admin
from django.urls import include
from django.urls import path

from accounts.views import AccountList

urlpatterns = [
    path('', AccountList.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('accounts/', include('accounts.urls')),
]
