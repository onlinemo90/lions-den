from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserCreationForm
from django.contrib.auth.forms import UserChangeForm

from .models import Zoo, ZooUser


class ZooUserBaseForm(forms.ModelForm):
	_zoos = forms.ModelMultipleChoiceField(
		queryset=Zoo.objects.all(),
		required=False,
		widget=FilteredSelectMultiple(
			verbose_name=_('Zoos'),
			is_stacked=False
		)
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance and self.instance.pk:
			self.fields['_zoos'].initial = self.instance._zoos.all()
	
	def save(self, commit=True):
		user = super().save(commit=False)
		user.save()
		if user.pk:
			user._zoos.set(self.cleaned_data['_zoos'])
			self.save_m2m()
		return user


class ZooUserChangeForm(ZooUserBaseForm, UserChangeForm):
	class Meta:
		model = ZooUser
		fields = ('email', 'first_name', 'last_name', '_zoos')


class ZooUserCreationForm(ZooUserBaseForm, UserCreationForm):
	class Meta:
		model = ZooUser
		fields = ('email', 'first_name', 'last_name', '_zoos')
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['password1'].required = False
		self.fields['password2'].required = False
	
	def save(self, commit=True):
		user = super().save(commit=False)
		random_password = ZooUser.objects.make_random_password()
		user.set_password(random_password)
		user.save()
		if user.pk:
			user.notify(
				subject='Account created',
				text_message=f"An account has been created for you in Lion's Den\nYour default password is: {random_password}",
				ignore_preferences=True
			)
		return user