import datetime
import html2text

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
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


class ZooAdminUserManager(BaseUserManager):
	def get_queryset(self):
		return super().get_queryset().filter(is_staff=True)


class ZooUser(AbstractUser):
	username = None
	email = models.EmailField(_('email address'), unique=True)
	first_name = models.CharField(blank=True, max_length=64)
	last_name = models.CharField(blank=True, max_length=64)
	
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []
	objects = ZooUserManager()
	admins = ZooAdminUserManager()
	
	def __str__(self):
		if self.first_name and self.last_name:
			return f'{self.first_name} {self.last_name}'
		elif self.first_name:
			return self.first_name
		elif self.last_name:
			return self.last_name
		return self.email
	
	@property
	def zoos(self):
		return Zoo.objects.all() if self.is_superuser else self._zoos.all()
	
	def has_access(self, zoo_id):
		return any(zoo.id==zoo_id for zoo in self.zoos)
	
	def notify(self, subject, text_message=None, html_message=None):
		type(self).notify_users([self], subject, text_message, html_message, notify_admins=False)
	
	@classmethod
	def notify_users(cls, users, subject, text_message=None, html_message=None, notify_separately=True, notify_admins=True):
		"""
		Sends an email to the relevant users
		:param users: queryset of users meant to be notified
		:param subject: subject line of email
		:param text_message: text version contents of the email. Will be auto-generated from html_message if not present
		:param html_message: HTML contents of the email
		:param notify_separately: if False, a single email will be sent with all users in To field, with admins in BCC
		:param notify_admins: if True, admins will be notified even if not in users
		:return: None
		"""
		
		if not text_message and not html_message:
			raise ValueError('Notification email cannot be sent without content')
		if not text_message:
			text_message = html2text.html2text(html_message)
		
		admins = ZooUser.admins.all()
		bcc_users = []
		
		if notify_admins:
			users = users.difference(admins)
		if notify_separately:
			mailing_lists = [(user,) for user in users]
			if notify_admins:
				mailing_lists.append(admins)
		else:
			mailing_lists = [users]
			if notify_admins:
				bcc_users = admins
		
		for mailing_list in mailing_lists:
			email_message = EmailMultiAlternatives(
				subject=subject,
				body=text_message,
				to=[user.email for user in mailing_list],
				bcc=[user.email for user in bcc_users],
			)
			if html_message:
				email_message.attach_alternative(html_message, 'text/html')
			email_message.send(fail_silently=True)
	
	@classmethod
	def notify_admins(cls, subject, text_message=None, html_message=None):
		cls.notify_users(
			users=cls.objects.none(),
			subject=subject,
			text_message=text_message,
			html_message=html_message,
			notify_admins=True
		)


class Zoo(models.Model):
	_id = models.AutoField(primary_key=True)
	id = models.CharField(unique=True, max_length=10)
	name = models.CharField(unique=True, max_length=128)
	encryption_key = models.CharField(unique=True, max_length=35)
	image = models.ImageField()
	date_joined = models.DateField(auto_now_add=True)
	last_commit_date = models.DateField(blank=True)
	
	users = models.ManyToManyField(ZooUser, related_name='_zoos')
	
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
			ZooUser.notify_admins(
				subject=f'Request for commit - {self.name}',
				html_message=render_to_string(
					'zoo_auth/emails/zoo_commit.html',
					{ 'zoo': self, 'user': user}
				)
			)
			self.last_commit_date = datetime.date.today()
			self.save()
		else:
			raise Exception('You cannot make any commits within 30 days of each other.\nLast commit: ' + str(self.last_commit_date))