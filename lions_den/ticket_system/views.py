from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic.list import ListView

from .models import Ticket
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView
from django.views.generic.list import ListView

from .models import Ticket
from .forms import TicketForm, CommentForm, UpdateTicketForm, AssignTicketForm


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
	
	def get_ajax(self, request, *args, **kwargs):
		if 'modal_new_ticket' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Create a new ticket',
					'form': TicketForm(),
					'submit_btn_name': 'create_ticket',
				}
			)
		return self.get_ajax_sub(request, *args, **kwargs)
	
	def post(self, request, *args, **kwargs):
		if 'create_ticket' in request.POST:
			form = TicketForm(request.POST)
			if form.is_valid():
				form.save(reporter=request.user)
				return redirect(to=reverse('ticket_view', kwargs={'pk': form.instance.id}))
		return self.post_sub(request, *args, **kwargs)
	
	def get_ajax_sub(self, request, *args, **kwargs):
		pass
	
	def post_sub(self, request, *args, **kwargs):
		pass


class TicketListView(BaseView, ListView):
	model = Ticket
	template_name = 'ticket_system/ticket_list.html'


class TicketView(BaseView, DetailView):
	model = Ticket
	template_name = 'ticket_system/ticket.html'
	
	def get_ticket(self, pk):
		return Ticket.objects.filter(id=pk).get()
	
	def get_ajax_sub(self, request, pk):
		if 'modal_new_comment' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Add comment',
					'form': CommentForm(),
					'submit_btn_name': 'create_comment',
				}
			)
		elif 'modal_edit_ticket' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Edit ticket',
					'form': TicketForm(instance=self.get_ticket(pk)),
					'submit_btn_name': 'edit_ticket',
				}
			)
		elif 'modal_update_ticket' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Update ticket',
					'form': UpdateTicketForm(instance=self.get_ticket(pk)),
					'submit_btn_name': 'update_ticket',
				}
			)
		elif 'modal_assign_ticket' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Assign ticket',
					'form': AssignTicketForm(instance=self.get_ticket(pk)),
					'submit_btn_name': 'assign_ticket',
				}
			)
	
	def post_sub(self, request, pk):
		if 'create_comment' in request.POST:
			form = CommentForm(request.POST)
			if form.is_valid():
				form.save(ticket=self.get_ticket(pk), creator=request.user)
				return self.redirect_to_self(request)
		elif 'edit_ticket' in request.POST:
			form = TicketForm(request.POST, instance=self.get_ticket(pk))
			if form.is_valid():
				form.save()
				return self.redirect_to_self(request)
		elif 'update_ticket' in request.POST:
			form = UpdateTicketForm(request.POST, instance=self.get_ticket(pk))
			if form.is_valid():
				form.save()
				return self.redirect_to_self(request)
		elif 'assign_ticket' in request.POST:
			form = AssignTicketForm(request.POST, instance=self.get_ticket(pk))
			if form.is_valid():
				form.save()
				return self.redirect_to_self(request)