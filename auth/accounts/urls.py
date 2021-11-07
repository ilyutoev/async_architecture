from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from accounts.views import SignUpView, EditView, AccountDelete, AccountData
from django.urls import reverse_lazy

urlpatterns = [
    path('sign_up/', SignUpView.as_view(), name='sign_up'),
    path('<int:pk>/edit/', EditView.as_view(), name='edit'),
    path('<int:pk>/delete/', AccountDelete.as_view(), name='delete'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('index')), name='logout'),
    path('account/', AccountData.as_view()),
]
