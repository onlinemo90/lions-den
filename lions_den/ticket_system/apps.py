from django.apps import AppConfig


class TicketSystemConfig(AppConfig):
    name = 'ticket_system'
    verbose_name = 'Ticket System'
    
    def ready(self):
        # noinspection PyUnresolvedReferences
        import ticket_system.signals
