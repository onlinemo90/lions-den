from django import forms

from .models import Ticket, Comment


class TicketForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = ('title', 'description')
	
	def save(self, reporter, commit=True):
		self.instance.reporter = reporter
		super().save(commit)


class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('text',)
	
	def save(self, ticket, creator, commit=True):
		self.instance.ticket = ticket
		self.instance.creator = creator
		super().save(commit)
