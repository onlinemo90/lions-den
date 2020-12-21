from django.urls import path
from django.shortcuts import redirect
import django.contrib.auth.views as auth_views
from . import views

urlpatterns = [
    path('', lambda request : redirect('login')),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]