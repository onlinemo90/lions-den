from django import forms
from django.utils import timezone

# noinspection PyUnresolvedReferences
from zoo_auth.models import ZooUser

from .models import Ticket, Comment


class TicketForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = ('app', 'title', 'type', 'priority', 'description')

	def save(self, reporter=None, commit=True):
		if reporter:
			self.instance.reporter = reporter
		super().save(commit)


class TicketAssigneeForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = ('assignee',)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['assignee'] = forms.ModelChoiceField(queryset=ZooUser.objects.filter(is_staff=True))
	
	def save(self, commit=True):
		super().save(commit=False)
		if self.instance.status == Ticket.Status.UNASSIGNED and self.instance.assignee is not None:
			self.instance.status = Ticket.Status.IN_ANALYSIS
		super().save(commit)


class TicketStatusForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = ('status',)
	
	def save(self, commit=True):
		super().save(commit=False)
		if self.instance.is_open() != Ticket.Status.is_open(self.initial['status']):
			self.instance.closed_date = timezone.now() if not self.instance.is_open() else None
		super().save(commit)


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
