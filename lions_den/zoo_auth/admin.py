from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Zoo, ZooUser
from .forms import ZooUserCreationForm, ZooUserChangeForm


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
			'fields': ('email', 'first_name', 'last_name', '_zoos')}
		 ),
	)
	filter_horizontal = ('groups', 'user_permissions', '_zoos')
	search_fields = ('email',)
	ordering = ('email',)


@admin.register(Zoo)
class ZooAdmin(admin.ModelAdmin):
	filter_horizontal = ('users',)
