from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import logout, get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import UpdateView

# noinspection PyUnresolvedReferences
from ticket_system.models import TicketActionNotification


def logout_view(request):
	logout(request)
	messages.info(request, 'You have been logged out')
	return redirect('login')


class HomeView(LoginRequiredMixin, TemplateView):
	template_name = 'zoo_auth/front_page.html'


class PreferencesView(LoginRequiredMixin, UpdateView):
	fields = ('notification_method',)
	template_name = 'zoo_auth/preferences.html'
	context_object_name = 'user'
	success_url = reverse_lazy('user_preferences')
	
	def get_object(self):
		return get_user_model().objects.get(id=self.request.user.id)


class NotificationsView(LoginRequiredMixin, ListView):
	template_name = 'zoo_auth/notifications.html'
	context_object_name = 'notifications'
	
	def get_queryset(self):
		return get_user_model().objects.none()
	
	def post(self, request):
		if request.is_ajax():
			if 'delete_notification' in request.POST:
				notification = TicketActionNotification.objects.get(id=request.POST.get('id'))
				if notification.user == request.user:
					notification.delete()
					return JsonResponse({})
