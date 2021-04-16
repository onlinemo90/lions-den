from django.db import models

# noinspection PyUnresolvedReferences
from zoo_auth.models import ZooUser


class Ticket(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=48)
	description = models.TextField()
	reporter = models.ForeignKey(ZooUser, related_name='reported_tickets', on_delete=models.PROTECT, blank=True, default=None)
	assignee = models.ForeignKey(ZooUser, related_name='assigned_tickets', on_delete=models.PROTECT, blank=True, default=None)
	created_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)
	closed_date = models.DateTimeField(blank=True)
	# TODO: add watchers
	# TODO: add fix versions
	
	def __str__(self):
		return str(self.id) + ' - ' + self.title


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