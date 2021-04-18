from django import forms

from .models import Ticket, Comment
from zoo_auth.models import ZooUser


class TicketForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = ('title', 'type', 'priority', 'description')
	
	def save(self, reporter, commit=True):
		self.instance.reporter = reporter
		super().save(commit)


class AssignTicketForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = ('assignee',)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['assignee'] = forms.ModelChoiceField(queryset=ZooUser.objects.filter(is_staff=True))
	
	def save(self, commit=True):
		super().save(commit)
		if self.instance.action == Ticket.Actions.WAIT:
			self.instance.action = Ticket.Actions.IN_ANALYSIS
			self.instance.save()


class UpdateTicketForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = ('status', 'action')


class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('text',)
	
	def save(self, ticket, creator, commit=True):
		self.instance.ticket = ticket
		self.instance.creator = creator
		super().save(commit)
