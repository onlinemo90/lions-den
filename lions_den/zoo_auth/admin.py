from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin, UserCreationForm

from .models import Zoo, ZooUser


class ZooUserChangeForm(forms.ModelForm):
	zoos = forms.ModelMultipleChoiceField(
		queryset=Zoo.objects.all(),
		required=False,
		widget=FilteredSelectMultiple(
			verbose_name=_('Zoos'),
			is_stacked=False
		)
	)
	
	class Meta:
		model = ZooUser
		fields=('zoos',)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance and self.instance.pk:
			self.fields['zoos'].initial = self.instance.zoos.all()
	
	def save(self, commit=True):
		user = super().save(commit=False)
		if commit:
			user.save()
		if user.pk:
			user.zoos.set(self.cleaned_data['zoos'])
			self.save_m2m()
		return user


class ZooUserCreationForm(UserCreationForm):
	zoos = forms.ModelMultipleChoiceField(
		queryset=Zoo.objects.all(),
		required=False,
		widget=FilteredSelectMultiple(
			verbose_name=_('Zoos'),
			is_stacked=False
		)
	)
	
	class Meta:
		model = ZooUser
		fields=('email', 'password1', 'password2', 'zoos')
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance and self.instance.pk:
			self.fields['zoos'].initial = self.instance.zoos.all()
	
	def save(self, commit=True):
		user = super().save(commit=False)
		user.save()
		if user.pk:
			user.zoos.set(self.cleaned_data['zoos'])
			self.save_m2m()
		return user


@admin.register(ZooUser)
class CustomUserAdmin(UserAdmin):
	model = ZooUser
	form = ZooUserChangeForm
	add_form = ZooUserCreationForm
	list_display = ('email', 'is_staff', 'is_active',)
	list_filter = ('email', 'is_staff', 'is_active',)
	fieldsets = (
		(None, {'fields': ('email',)}),
		(_('Personal info'), {'fields': ('first_name', 'last_name')}),
		(_('Permissions'), {
			'fields': ('is_active', 'is_superuser', 'zoos', 'groups', 'user_permissions'),
		}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'password1', 'password2', 'zoos')}
		 ),
	)
	filter_horizontal = ('groups', 'user_permissions', 'zoos')
	search_fields = ('email',)
	ordering = ('email',)


@admin.register(Zoo)
class ZooAdmin(admin.ModelAdmin):
	filter_horizontal = ('users',)
