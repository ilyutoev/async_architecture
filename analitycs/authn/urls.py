from django.urls import path

from authn.views import login, redirect_to, oauth_callback

urlpatterns = [
    path('login/', login, name='login'),
    path('redirect_to/', redirect_to, name='redirect'),
    path('oauth_callback/', oauth_callback, name='callback'),
]
