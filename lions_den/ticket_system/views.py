import functools
import operator

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView
from django.db.models import Q

from .models import Ticket, Comment
from .forms import TicketForm, CommentForm, TicketStatusForm, TicketAssigneeForm, TicketAttachmentForm


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
				form.save(updater=request.user)
				return redirect(to=reverse('ticket_page', kwargs={'pk': form.instance.id}))
		return self.post_sub(request, *args, **kwargs)
	
	def get_ajax_sub(self, request, *args, **kwargs):
		pass
	
	def post_sub(self, request, *args, **kwargs):
		pass


class TicketListView(BaseView):
	template_name = 'ticket_system/ticket_list.html'
	default_queryset = Ticket.objects.all().order_by('-id')
	
	def get(self, request):
		return render(
			request=request,
			template_name=self.template_name,
			context={
				'ticket_model': Ticket,
				'tickets': Ticket.objects.all().order_by('-id')
			}
		)
	
	def get_ajax_sub(self, request):
		filtered_tickets = functools.reduce(
			lambda ticket_list, field_dict: ticket_list.filter(**field_dict),
			[{field: request.GET.get(field)} for field in request.GET if hasattr(Ticket, field)],
			self.default_queryset
		)
		if '__user_is_assignee__' in request.GET:
			filtered_tickets = filtered_tickets.filter(assignee=request.user)
		if '__user_is_creator__' in request.GET:
			filtered_tickets = filtered_tickets.filter(reporter=request.user)
		if '__user_is_watcher__' in request.GET:
			filtered_tickets = filtered_tickets.filter(watchers=request.user.id)
		
		# Keyword search
		if '__search__' in request.GET:
			keywords = request.GET.get('__search__').split(' ')
			filtered_tickets = filtered_tickets.filter(
				functools.reduce(lambda x, y: x | y, (Q(title__icontains=word) for word in keywords)) |
				functools.reduce(lambda x, y: x | y, (Q(description__icontains=word) for word in keywords)) |
				functools.reduce(lambda x, y: x | y, (Q(comments__text__icontains=word) for word in keywords))
			).distinct()
		
		return render(
			request=request,
			template_name='ticket_system/ticket_list_table.html',
			context={
				'tickets': filtered_tickets
			}
		)


class TicketView(BaseView, DetailView):
	model = Ticket
	template_name = 'ticket_system/ticket.html'
	context_object_name = 'ticket'
	
	def get_object(self):
		return Ticket.objects.filter(id=self.kwargs['pk']).get()
	
	def get_context_data(self, **kwargs):
		return super().get_context_data(
			user_is_watcher=(self.request.user in self.get_object().watchers.all()),
			comment_form=CommentForm(prefix='comment'),
			attachment_form=TicketAttachmentForm(prefix='attachment')
		)
	
	def get_ajax_sub(self, request, pk):
		if 'modal_edit_ticket' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Edit ticket',
					'form': TicketForm(instance=self.get_object()),
					'submit_btn_name': 'edit_ticket',
				}
			)
		elif 'modal_ticket_status' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Update ticket',
					'form': TicketStatusForm(instance=self.get_object(), user=request.user),
					'submit_btn_name': 'update_ticket_status',
				}
			)
		elif 'modal_assign_ticket' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Assign ticket',
					'form': TicketAssigneeForm(instance=self.get_object()),
					'submit_btn_name': 'assign_ticket',
				}
			)
		elif 'modal_new_comment' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Add comment',
					'form': CommentForm(prefix='comment'),
					'submit_btn_name': 'create_comment',
				}
			)
		elif 'modal_edit_comment' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Edit comment',
					'form': CommentForm(instance=Comment.objects.filter(id=request.GET.get('id')).get(), prefix='comment'),
					'submit_btn_name': 'edit_comment',
				}
			)
	
	def post_sub(self, request, pk):
		if 'edit_ticket' in request.POST:
			form = TicketForm(request.POST, instance=self.get_object())
			if form.is_valid():
				form.save(request.user)
				return self.redirect_to_self(request)
		elif 'update_ticket_status' in request.POST:
			form = TicketStatusForm(request.POST, instance=self.get_object(), user=request.user)
			if form.is_valid():
				form.save(request.user)
				return self.redirect_to_self(request)
		elif 'assign_ticket' in request.POST:
			form = TicketAssigneeForm(request.POST, instance=self.get_object())
			if form.is_valid():
				form.save(request.user)
				return self.redirect_to_self(request)
		elif 'add_comment' in request.POST:
			form = CommentForm(request.POST, prefix='comment')
			if form.is_valid():
				form.save(ticket=self.get_object(), creator=request.user)
				return self.redirect_to_self(request)
		elif 'edit_comment' in request.POST:
			form = CommentForm(request.POST, prefix='comment')
			if form.is_valid():
				form.save()
				return self.redirect_to_self(request)
		elif 'add_attachment' in request.POST:
			comment_form = CommentForm(request.POST, prefix='comment')
			attachment_form = TicketAttachmentForm(request.POST, request.FILES, prefix='attachment')
			if comment_form.is_valid() and attachment_form.is_valid():
				comment_form.save(ticket=self.get_object(), creator=request.user)
				attachment_form.save(ticket=self.get_object(), comment=comment_form.instance, uploader=request.user)
				return self.redirect_to_self(request)

	def post_ajax(self, request, pk):
		if 'set_watcher_status' in request.POST:
			# tickets are added to user's watched_tickets and not the other way around to prevent updating the ticket
			ticket = self.get_object()
			if request.POST.get('set_watcher_status') and ticket not in request.user.watched_tickets.all():
				request.user.watched_tickets.add(ticket)
			elif ticket in request.user.watched_tickets.all():
				request.user.watched_tickets.remove(ticket)
			request.user.save()
			return JsonResponse({'user_is_watcher': (request.user in ticket.watchers.all())})