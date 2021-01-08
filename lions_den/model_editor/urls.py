from django.urls import path
from .views import zoos_index, zoo_home, species, species_list

urlpatterns = [
    path('', zoos_index),
    path('<str:zoo_id>/', zoo_home),
    path('<str:zoo_id>/species/', species_list, name='species_list'),
    path('<str:zoo_id>/species/<str:species_id>', species),
]