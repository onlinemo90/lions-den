import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class ZooUserManager(BaseUserManager):
	""" Custom user model manager where email is the unique identifier for authentication """
	def create_user(self, email, password, **extra_fields):
		if not email:
			raise ValueError(_('The Email must be set'))
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError(_('Superuser must have is_staff=True.'))
		if extra_fields.get('is_superuser') is not True:
			raise ValueError(_('Superuser must have is_superuser=True.'))
		return self.create_user(email, password, **extra_fields)


class ZooUser(AbstractUser):
	username = None
	email = models.EmailField(_('email address'), unique=True)
	
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []
	objects = ZooUserManager()

	def __str__(self):
		return self.email
	
	@property
	def allowed_zoos(self):
		return Zoo.objects.all() if self.is_superuser else self.zoos.all()
	
	def has_access(self, zoo_id):
		return any(zoo.id==zoo_id for zoo in self.allowed_zoos)
	

class Zoo(models.Model):
	_id = models.AutoField(primary_key=True)
	id = models.CharField(unique=True, max_length=10)
	name = models.CharField(unique=True, max_length=128)
	encryption_key = models.CharField(unique=True, max_length=35)
	image = models.ImageField()
	date_joined = models.DateField(auto_now_add=True)
	last_commit_date = models.DateField(blank=True)
	
	users = models.ManyToManyField(ZooUser, related_name='zoos')
	
	def __str__(self):
		return self.name
	
	def can_commit(self):
		return self.days_until_commit_allowed() <= 0
	
	def days_until_commit_allowed(self):
		if self.last_commit_date:
			return (self.last_commit_date + datetime.timedelta(days=30) - datetime.date.today()).days
		else:
			return 0
	
	def commit_to_zooverse(self, user):
		if self.can_commit():
			# Send notification email
			send_mail(
				subject=f'Request for commit - {self.name}',
				message=f'Commit Request received:\n\tZoo name:\t{self.name}\n\tZoo ID:\t{self.id}\n\tUser:\t{user.email}',
				from_email='contact@zooverse.org',
				recipient_list=['pedro.ferreira@zooverse.org', 'moritz.fritzsche@zooverse.org'],
				fail_silently=False,
			)
			self.last_commit_date = datetime.date.today()
			self.save()
		else:
			raise Exception('You cannot make any commits within 30 days of each other.\nLast commit: ' + str(self.last_commit_date))