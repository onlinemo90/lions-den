from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin, UserCreationForm
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


class ZooUserCreationForm(UserCreationForm, ZooUserBaseForm):
	class Meta:
		model = ZooUser
		fields = ('email', 'password1', 'password2', '_zoos')


@admin.register(ZooUser)
class ZoomUserAdmin(UserAdmin):
	model = ZooUser
	form = ZooUserChangeForm
	add_form = ZooUserCreationForm
	list_display = ('email', 'is_staff', 'is_active',)
	list_filter = ('email', 'is_staff', 'is_active',)
	fieldsets = (
		(None, {'fields': ('email',)}),
		(_('Personal info'), {'fields': ('first_name', 'last_name')}),
		(_('Permissions'), {
			'fields': ('is_active', 'is_staff', 'is_superuser', '_zoos'),
		}),
		(_('Dates'), {'fields': ('last_login', 'date_joined')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'password1', 'password2', '_zoos')}
		 ),
	)
	filter_horizontal = ('groups', 'user_permissions', '_zoos')
	search_fields = ('email',)
	ordering = ('email',)


@admin.register(Zoo)
class ZooAdmin(admin.ModelAdmin):
	filter_horizontal = ('users',)
