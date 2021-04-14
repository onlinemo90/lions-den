from django.db import models

# noinspection PyUnresolvedReferences
from zoo_auth.models import ZooUser


class Ticket(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=48)
	description = models.TextField()
	reporter = models.ForeignKey(to=ZooUser, related_name='reporter', on_delete=models.PROTECT, null=False)
	assignee = models.ForeignKey(to=ZooUser, related_name='assignee', on_delete=models.PROTECT, null=True, default=None)
	created_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)
	# TODO: add watchers
	
	def __str__(self):
		return str(self.id) + ' - ' + self.title


class Comment(models.Model):
	id = models.AutoField(primary_key=True)
	ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
	creator = models.ForeignKey(to=ZooUser, related_name='creator', on_delete=models.PROTECT)
	text = models.TextField()
	added_date = models.DateTimeField(auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.text