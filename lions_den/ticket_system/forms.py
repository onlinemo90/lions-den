from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

# noinspection PyUnresolvedReferences
from zoo_auth.models import ZooUser

from .models import Ticket, Comment, TicketAttachment


class BaseTicketForm(forms.ModelForm):
	def save(self, updater, commit=True):
		self.instance.last_updater = updater
		super().save(commit)


class TicketForm(BaseTicketForm):
	class Meta:
		model = Ticket
		fields = ('app', 'title', 'type', 'priority', 'description')
	
	def save(self, updater, commit=True):
		if not self.instance.pk: # new ticket
			self.instance.reporter = updater
			super().save(updater, commit)
			self.instance.watchers.add(updater)
			self.instance.save()
		else:
			super().save(updater, commit)


class TicketAssigneeForm(BaseTicketForm):
	class Meta:
		model = Ticket
		fields = ('assignee',)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['assignee'] = forms.ModelChoiceField(queryset=get_user_model().objects.filter(is_staff=True))
	
	def save(self, updater, commit=True):
		super().save(updater=updater, commit=False)
		if self.instance.status == Ticket.Status.UNASSIGNED and self.instance.assignee is not None:
			self.instance.status = Ticket.Status.IN_ANALYSIS
		super().save(updater=updater, commit=commit)


class TicketStatusForm(BaseTicketForm):
	class Meta:
		model = Ticket
		fields = ('status',)
	
	def save(self, updater, commit=True):
		super().save(updater=updater, commit=False)
		if self.instance.is_open() != Ticket.Status.is_open(self.initial['status']):
			self.instance.closed_date = timezone.now() if not self.instance.is_open() else None
		super().save(updater=updater, commit=commit)


class CommentForm(forms.ModelForm):
	id = forms.CharField(widget=forms.HiddenInput, required=False)
	class Meta:
		model = Comment
		fields = ('id', 'text')
		widgets = {
			'text': forms.Textarea(attrs={'rows': 3}),
		}
		labels = {
			'text': 'Comment'
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.data and self.data.get('id'): # to allow for editing comments
			self.instance = self._meta.model.objects.filter(id=self.data.get('id')).get()
			
	def save(self, ticket=None, creator=None, commit=True):
		if ticket:
			self.instance.ticket = ticket
		if creator:
			self.instance.creator = creator
		super().save(commit)
		
		# Add comment creator as ticket watcher
		self.instance.ticket.watchers.add(self.instance.creator)
		
		# Update last updater and last updated date on host ticket
		self.instance.ticket.last_updater = self.instance.creator
		self.instance.ticket.save()


class TicketAttachmentForm(forms.ModelForm):
	class Meta:
		model = TicketAttachment
		fields = ('file',)
	
	def save(self, ticket, uploader, commit=True):
		self.instance.name = self.instance.file.file.name
		self.instance.ticket = ticket
		self.instance.uploader = uploader
		super().save(commit)