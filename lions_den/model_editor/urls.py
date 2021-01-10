from django.urls import path
from .views import zoos_index, zoo_home, species_page, species_list, attributes_list

urlpatterns = [
    path('', zoos_index),
    path('<str:zoo_id>/', zoo_home),
    path('<str:zoo_id>/species/', species_list, name='species_list'),
    path('<str:zoo_id>/species/<str:species_id>', species_page),
    path('<str:zoo_id>/attributes/', attributes_list, name='attributes_list'),
]