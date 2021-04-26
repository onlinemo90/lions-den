from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.template.loader import render_to_string

# noinspection PyUnresolvedReferences
from zoo_auth.models import ZooUser

from .models import Ticket, Comment


def get_field_display(instance, field):
	if hasattr(instance, f'get_{field.name}_display'):
		return getattr(instance, f'get_{field.name}_display')()
	return getattr(instance, field.name)

def get_instance_changes(new_instance, old_instance=None):
	changes = {}
	for field in new_instance.notification_fields:
		if not old_instance or getattr(old_instance, field.name) != getattr(new_instance, field.name):
			changes[field.verbose_name] = {}
			changes[field.verbose_name]['new_value'] = get_field_display(new_instance, field)
			if old_instance:
				changes[field.verbose_name]['old_value'] = get_field_display(old_instance, field)
	return changes

@receiver(pre_save, sender=Ticket)
def notify_ticket_changes(sender, instance, **kwargs):
	try:
		old_ticket = sender.objects.get(pk=instance.pk)
	except sender.DoesNotExist:
		ZooUser.notify_users(
			users=ZooUser.objects.filter(id=instance.reporter.id),
			subject=f'{instance.reporter} created a ticket: {instance.title}',
			html_message=render_to_string(
				'ticket_system/emails/notification.html',
				{'context': get_instance_changes(instance)}
			)
		)
	else:
		changes = get_instance_changes(instance, old_ticket)
		if changes:
			ZooUser.notify_users(
				users=instance.watchers.all(),
				subject=f'{instance.last_updater} edited ticket: {instance.title}',
				html_message=render_to_string(
					'ticket_system/emails/notification.html',
					{'context': changes, 'edit_instance': True}
				)
			)

@receiver(pre_save, sender=Comment)
def notify_comment_changes(sender, instance, **kwargs):
	try:
		old_comment = sender.objects.get(pk=instance.pk)
	except sender.DoesNotExist:
		ZooUser.notify_users(
			users=instance.ticket.watchers.all(),
			subject=f'{instance.creator} added a comment on ticket: {instance.ticket}',
			html_message=render_to_string(
				'ticket_system/emails/notification.html',
				{'context': get_instance_changes(instance)}
			)
		)
	else:
		changes = get_instance_changes(instance, old_comment)
		if changes:
			ZooUser.notify_users(
				users=instance.ticket.watchers.all(),
				subject=f'{instance.creator} edited a comment in ticket: {instance.ticket}',
				html_message=render_to_string(
					'ticket_system/emails/notification.html',
					{'context': changes, 'edit_instance': True}
				)
			)
