from django.shortcuts import redirect
from django.contrib.auth import logout, get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView


def logout_view(request):
	logout(request)
	messages.info(request, 'You have been logged out')
	return redirect('login')


class EditPreferencesView(UpdateView):
	model = get_user_model()
	fields = ('wants_email_notifications',)
	template_name = 'zoo_auth/edit_preferences.html'
	
	def get_success_url(self):
		return reverse_lazy('edit_preferences', kwargs={'pk': self.kwargs['pk']})