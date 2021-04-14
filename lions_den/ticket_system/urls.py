from django.urls import path

from .views import TicketListView

urlpatterns = [
	path('', TicketListView.as_view(), name='ticket_list'),
]
