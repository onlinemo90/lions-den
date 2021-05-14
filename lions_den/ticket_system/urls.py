from django.urls import path

from .views import TicketListView, TicketView

urlpatterns = [
	path('', TicketListView.as_view(), name='ticket_list'),
	path('browse/<int:pk>', TicketView.as_view(), name='ticket_page')
]
