from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class TrackedFieldsModel(models.Model):
	class Meta:
		abstract = True
	
	def save(self, *args, **kwargs):
		action_ticket = self if type(self) == Ticket else self.ticket
		ticket_changes = []
		if self.pk: # pre-existing model instance
			old_instance = type(self).objects.get(pk=self.pk)
			
			super().save(*args, **kwargs)
			
			ticket_action = TicketAction(ticket=action_ticket, target=self, user=action_ticket.last_updater, type=TicketAction.Type.EDIT)
			for tracked_field in self.tracked_fields:
				old_value, new_value = getattr(old_instance, tracked_field.name), getattr(self, tracked_field.name)
				if old_value != new_value:
					ticket_changes.append(TicketChange(action=ticket_action, field=tracked_field.name, old_value=old_value, new_value=new_value))
		else: # new model instance
			super().save(*args, **kwargs)
			ticket_action = TicketAction(ticket=action_ticket, target=self, user=action_ticket.last_updater, type=TicketAction.Type.CREATE)
			for tracked_field in self.tracked_fields:
				new_value = getattr(self, tracked_field.name)
				if new_value:
					ticket_changes.append(TicketChange(action=ticket_action, field=tracked_field.name, new_value=new_value))
		
		if ticket_changes:
			ticket_action.save()
			for ticket_change in ticket_changes:
				ticket_change.save()
			ticket_action.trigger_notifications()


class Ticket(TrackedFieldsModel):
	class App(models.TextChoices):
		ZOOVERSE = 'ZV', _('Zooverse')
		LIONS_DEN = 'LD', _("Lion's Den")
	
	class Status(models.TextChoices):
		UNASSIGNED = 'U', _('Unassigned')
		IN_ANALYSIS = 'A', _('In Analysis')
		IN_DEVELOPMENT = 'D', _('In Development')
		CANCELLED = 'CA', _('Cancelled')
		REJECTED = 'R', _('Rejected')
		COMPLETED = 'CO', _('Completed')
		
		@classmethod
		def is_open(cls, status_str):
			return status_str not in (cls.CANCELLED, cls.REJECTED, cls.COMPLETED)
	
	class Type(models.TextChoices):
		BUG = 'B', _('Bug')
		FEATURE = 'F', _('Feature Request')
		IMPROVEMENT = 'I', _('Improvement Request')
		MAINTENANCE = 'M', _('Maintenance')
	
	class Priority(models.IntegerChoices):
		TRIVIAL = 0, _('Trivial')
		LOW = 1, _('Low')
		MEDIUM = 2, _('Medium')
		HIGH = 3, _('High')
		CRITICAL = 4, _('Critical')
	
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=128, verbose_name='Title')
	description = models.TextField(verbose_name='Description')
	
	app = models.CharField(max_length=2, choices=App.choices, blank=False, verbose_name='App')
	status = models.CharField(max_length=2, choices=Status.choices, default=Status.UNASSIGNED, blank=False, verbose_name='Status')
	type = models.CharField(max_length=2, choices=Type.choices, blank=False, verbose_name='Type')
	priority = models.IntegerField(choices=Priority.choices, blank=False, verbose_name='Priority')
	
	reporter = models.ForeignKey(get_user_model(), related_name='reported_tickets', on_delete=models.PROTECT, blank=True, null=True, default=None, verbose_name='Reporter')
	assignee = models.ForeignKey(get_user_model(), related_name='assigned_tickets', on_delete=models.PROTECT, blank=True, null=True, default=None, verbose_name='Assignee')
	last_updater = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, blank=True, null=True, default=None, verbose_name='Last Updater')
	watchers = models.ManyToManyField(get_user_model(), related_name='watched_tickets', blank=True, default=None)
	
	created_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)
	closed_date = models.DateTimeField(blank=True, null=True)
	
	# Define the fields whose changes are tracked
	tracked_fields = [title, description, app, status, type, priority, assignee]
	
	def __str__(self):
		return f'#{self.id} - {self.title}'
	
	def is_open(self):
		return self.Status.is_open(self.status)
	
	def get_status_colour(self):
		if self.status == self.Status.UNASSIGNED:
			return'var(--info)'
		elif self.status == self.Status.IN_ANALYSIS:
			return 'var(--cyan)'
		elif self.status == self.Status.IN_DEVELOPMENT:
			return 'var(--primary)'
		elif self.status in (self.Status.CANCELLED, self.Status.REJECTED):
			return 'var(--danger)'
		elif self.status == self.Status.COMPLETED:
			return 'var(--success)'


class Comment(TrackedFieldsModel):
	id = models.AutoField(primary_key=True)
	ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
	creator = models.ForeignKey(get_user_model(), related_name='comments', on_delete=models.PROTECT)
	text = models.TextField(verbose_name='Contents')
	added_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)

	tracked_fields = [text]

	def __str__(self):
		return self.text
	
	def has_been_edited(self):
		return self.added_date != self.last_updated_date


class TicketAttachment(models.Model):
	ticket = models.ForeignKey(Ticket, related_name='attachments', on_delete=models.CASCADE)
	comment = models.ForeignKey(Comment, related_name='attachments', on_delete=models.CASCADE)
	name = models.CharField(max_length=128, blank=False)
	file = models.FileField(blank=False)
	uploader = models.ForeignKey(get_user_model(), related_name='attachments', on_delete=models.PROTECT)
	uploaded_date = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.name


class TicketAction(models.Model):
	class Type(models.TextChoices):
		CREATE = 'CREATE', _('created')
		EDIT = 'EDIT', _('edited')
	
	ticket = models.ForeignKey(Ticket, related_name='actions', on_delete=models.CASCADE)
	user = models.ForeignKey(get_user_model(), related_name='ticket_actions', on_delete=models.PROTECT)
	timestamp = models.DateTimeField(auto_now_add=True)
	type = models.CharField(max_length=6, choices=Type.choices, blank=False)
	
	# Model that is the target of the change, e.g. Ticket, Comment, etc.
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	target = GenericForeignKey('content_type', 'object_id')
	
	def __str__(self):
		return f'{self.target}: {self.user} {self._get_predicate_str(as_html=False)}'
	
	def is_creation(self):
		return self.type == self.Type.CREATE
	
	def _get_predicate_str(self, as_html=False):
		predicate_str = ''
		target_str = f'<b>{self.target}</b>' if as_html else f'{self.target}'
		if type(self.target) == Ticket:
			if self.type == self.Type.CREATE:
				predicate_str = f'created {target_str}'
			elif self.type == self.Type.EDIT:
				predicate_str = f'made changes to {target_str}'
		elif type(self.target) == Comment:
			if self.type == self.Type.CREATE:
				predicate_str = 'added a comment'
				num_attachments = len(self.target.attachments.all())
				if num_attachments == 1:
					predicate_str += ' with an attachment'
				elif num_attachments > 1:
					predicate_str += f' with {num_attachments} attachments'
			elif self.type == self.Type.EDIT:
				predicate_str = 'edited a comment'
		return predicate_str
	
	def as_html(self):
		return f'<b>{self.user}</b> {self._get_predicate_str(as_html=True)}'
	
	def trigger_notifications(self):
		# In-app notifications
		for user in self.ticket.watchers.all():
			if user != self.user: # users shouldn't be notified of their own actions
				TicketActionNotification(
					user=self.user,
					action=self
				).save()
		
		# Email notifications
		get_user_model().notify_users(
			users=self.ticket.watchers,
			subject=str(self),
			html_message=render_to_string(
				template_name='ticket_system/emails/notification.html',
				context={'action': self}
			)
		)


class TicketChange(models.Model):
	action = models.ForeignKey(TicketAction, related_name='changes', on_delete=models.CASCADE)
	field = models.CharField(max_length=32, blank=False)
	old_value = models.TextField(blank=True, null=True)
	new_value = models.TextField(blank=True, null=True)
	
	def _get_field(self):
		return getattr(type(self.action.target), self.field).field
	
	def get_field_name(self):
		return self._get_field().verbose_name
	
	def _get_value_display(self, stored_value):
		field = self._get_field()
		if field.choices:
			for choice_key, choice_value in field.choices:
				if str(choice_key) == str(stored_value):
					return choice_value
		return stored_value
	
	def get_old_value_display(self):
		return self._get_value_display(self.old_value)
	
	def get_new_value_display(self):
		return self._get_value_display(self.new_value)


class TicketActionNotification(models.Model):
	user = models.ForeignKey(get_user_model(), related_name='ticket_notifications', on_delete=models.CASCADE)
	action = models.ForeignKey(TicketAction, related_name='user_notifications', on_delete=models.CASCADE)
	
	def as_html(self):
		return self.action.as_html()
	
	def timestamp(self):
		return self.action.timestamp
	
	def url(self):
		return reverse_lazy('ticket_page', kwargs={'pk': self.action.ticket.id})