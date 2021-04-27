from django.db import models
from django.utils.translation import gettext_lazy as _

# noinspection PyUnresolvedReferences
from zoo_auth.models import ZooUser


class Ticket(models.Model):
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
	
	reporter = models.ForeignKey(ZooUser, related_name='reported_tickets', on_delete=models.PROTECT, blank=True, null=True, default=None, verbose_name='Reporter')
	assignee = models.ForeignKey(ZooUser, related_name='assigned_tickets', on_delete=models.PROTECT, blank=True, null=True, default=None, verbose_name='Assignee')
	last_updater = models.ForeignKey(ZooUser, on_delete=models.PROTECT, blank=True, null=True, default=None, verbose_name='Last Updater')
	watchers = models.ManyToManyField(ZooUser, related_name='watched_tickets', blank=True, default=None)
	
	created_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)
	closed_date = models.DateTimeField(blank=True, null=True)
	
	# Define the fields that, when changed, will trigger notifications
	notification_fields = [title, description, app, status, type, priority, assignee]
	
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


class Comment(models.Model):
	id = models.AutoField(primary_key=True)
	ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
	creator = models.ForeignKey(ZooUser, related_name='comments', on_delete=models.PROTECT)
	text = models.TextField(verbose_name='Contents')
	added_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)

	notification_fields = [text]

	def __str__(self):
		return self.text


class TicketAttachment(models.Model):
	ticket = models.ForeignKey(Ticket, related_name='attachments', on_delete=models.CASCADE)
	name = models.CharField(max_length=128, blank=False)
	file = models.FileField(blank=False)
	uploader = models.ForeignKey(ZooUser, related_name='attachments', on_delete=models.PROTECT)
	uploaded_date = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.name
