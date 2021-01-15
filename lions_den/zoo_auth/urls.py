from django.urls import path
import django.contrib.auth.views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='zoo_auth/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='zoo_auth/change_password.html'), name='change-password'),
]