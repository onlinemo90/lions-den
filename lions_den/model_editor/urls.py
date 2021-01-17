from django.urls import path
from .views import zoos_index, zoo_home, species_page, individual_page, species_list, individuals_list, attributes_list

urlpatterns = [
    path('', zoos_index, name='zoo_index'),
    path('<str:zoo_id>/', zoo_home),
    
    path('<str:zoo_id>/species/', species_list, name='species_list'),
    path('<str:zoo_id>/species/<str:species_id>', species_page),
    
    path('<str:zoo_id>/individuals/', individuals_list, name='individuals_list'),
    path('<str:zoo_id>/individuals/<str:individual_id>', individual_page),
    
    path('<str:zoo_id>/attributes/', attributes_list, name='attributes_list'),
]