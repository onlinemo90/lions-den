from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic.list import ListView

from .models import Ticket


class BaseView(LoginRequiredMixin, View):
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		""" Restrict access to view only to logged-in users """
		# Check user permissions
		if not request.user.is_authenticated:
			return redirect('home')
		
		# Dispatch as usual but if an AJAX request, then redirect to [http_method]_ajax
		if request.method.lower() in self.http_method_names:
			method_name = request.method.lower()
			if request.is_ajax():
				method_name += '_ajax'
			handler = getattr(self, method_name, self.http_method_not_allowed)
		else:
			handler = self.http_method_not_allowed
		return handler(request, *args, **kwargs)
	
	def redirect_to_self(self, request):
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TicketListView(BaseView, ListView):
	model = Ticket
