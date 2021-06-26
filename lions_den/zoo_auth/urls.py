from django.urls import path, reverse_lazy
import django.contrib.auth.views as auth_views

from . import views

urlpatterns = [
	path('', views.HomeView.as_view(), name='home'),
	path('login/', auth_views.LoginView.as_view(template_name='zoo_auth/login.html', redirect_authenticated_user=True), name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('user/change-password/', auth_views.PasswordChangeView.as_view(template_name='zoo_auth/change_password.html', success_url=reverse_lazy('zoo_index')), name='change_password'),
	path('user/preferences/', views.PreferencesView.as_view(), name='user_preferences'),
	path('user/notifications/', views.NotificationsView.as_view(), name='user_notifications'),
]
