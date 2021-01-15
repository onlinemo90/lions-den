from django.urls import path
import django.contrib.auth.views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='zoo_auth/auth.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change-password'),
]