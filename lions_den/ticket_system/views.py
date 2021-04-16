from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView
from django.views.generic.list import ListView

from .models import Ticket
from .forms import TicketForm, CommentForm


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
	template_name = 'ticket_system/ticket_list.html'

	def get_ajax(self, request):
		if 'modal_new_ticket':
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Create a new ticket',
					'form': TicketForm(),
					'submit_btn_name': 'create_ticket',
				}
			)
	
	def post(self, request):
		if 'create_ticket' in request.POST:
			form = TicketForm(request.POST)
			if form.is_valid():
				form.save(reporter=request.user)
				return redirect('ticket_view')


class TicketView(BaseView, DetailView):
	model = Ticket
	template_name = 'ticket_system/ticket.html'
	
	def get_ajax(self, request, pk):
		if 'modal_new_comment':
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Add comment',
					'form': CommentForm(),
					'submit_btn_name': 'create_comment',
				}
			)
	
	def post(self, request, pk):
		if 'create_comment':
			form = CommentForm(request.POST)
			if form.is_valid():
				form.save(ticket=Ticket.objects.filter(id=pk).get(), creator=request.user)
				return self.redirect_to_self(request)
	
