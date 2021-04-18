from django.db import models
from django.utils.translation import gettext_lazy as _

# noinspection PyUnresolvedReferences
from zoo_auth.models import ZooUser


class Ticket(models.Model):
	class Statuses(models.TextChoices):
		OPEN = 'O', _('Open')
		CLOSED = 'C', _('Closed')
	
	class Types(models.TextChoices):
		BUG = 'B', _('Bug')
		FEATURE = 'F', _('Feature Request')
		IMPROVEMENT = 'I', _('Improvement Request')
		MAINTENANCE = 'M', _('Maintenance')
	
	class Priorities(models.IntegerChoices):
		TRIVIAL = 0, _('Trivial')
		LOW = 1, _('Low')
		MEDIUM = 2, _('Medium')
		HIGH = 3, _('High')
		CRITICAL = 4, _('Critical')
	
	class Actions(models.TextChoices):
		WAIT = 'W', _('Awaiting assignment')
		IN_ANALYSIS = 'A', _('In Analysis')
		IN_DEVELOPMENT = 'D', _('In Development')
		COMPLETED = 'C', _('Completed')
		REJECTED = 'R', _('Rejected')
	
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=48)
	description = models.TextField()
	reporter = models.ForeignKey(ZooUser, related_name='reported_tickets', on_delete=models.PROTECT, blank=True, null=True, default=None)
	assignee = models.ForeignKey(ZooUser, related_name='assigned_tickets', on_delete=models.PROTECT, blank=True, null=True, default=None)
	created_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)
	closed_date = models.DateTimeField(blank=True, null=True)
	
	status = models.CharField(max_length=2, choices=Statuses.choices, blank=False)
	type = models.CharField(max_length=2, choices=Types.choices, blank=False)
	priority = models.IntegerField(choices=Priorities.choices, blank=False)
	action = models.CharField(max_length=2, choices=Actions.choices, default=Actions.WAIT, blank=False)
	# TODO: add watchers
	# TODO: add fix versions
	
	def __str__(self):
		return str(self.id) + ' - ' + self.title

	def is_open(self):
		return self.status == 'O'


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