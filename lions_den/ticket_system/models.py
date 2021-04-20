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
	title = models.CharField(max_length=128)
	description = models.TextField()
	reporter = models.ForeignKey(ZooUser, related_name='reported_tickets', on_delete=models.PROTECT, blank=True, null=True, default=None)
	assignee = models.ForeignKey(ZooUser, related_name='assigned_tickets', on_delete=models.PROTECT, blank=True, null=True, default=None)
	created_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)
	closed_date = models.DateTimeField(blank=True, null=True)

	app = models.CharField(max_length=2, choices=App.choices, blank=False)
	status = models.CharField(max_length=2, choices=Status.choices, default=Status.UNASSIGNED, blank=False)
	type = models.CharField(max_length=2, choices=Type.choices, blank=False)
	priority = models.IntegerField(choices=Priority.choices, blank=False)

	watchers = models.ManyToManyField(to=ZooUser, related_name='watched_tickets', blank=True, default=None)
	
	def __str__(self):
		return str(self.id) + ' - ' + self.title

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
	text = models.TextField()
	added_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.text


# TODO: Add release versions