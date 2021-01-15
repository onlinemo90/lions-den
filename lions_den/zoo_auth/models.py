from django.utils.translation import ugettext_lazy as _
from django.db import models
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


class Zoo(models.Model):
	_id = models.AutoField(primary_key=True)
	id = models.CharField(unique=True, max_length=10)
	name = models.CharField(unique=True, max_length=128)
	encryption_key = models.CharField(unique=True, max_length=35)
	image = models.ImageField()
	date_joined = models.DateField(auto_now_add=True)
	
	users = models.ManyToManyField(ZooUser, related_name='zoos')
	
	def __str__(self):
		return self.name