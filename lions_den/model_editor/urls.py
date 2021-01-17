from django.urls import path
from .views import zoos_index, zoo_home, species_page, individual_page, species_list, individuals_list, attribute_category_list

urlpatterns = [
    path('', zoos_index),
    path('<str:zoo_id>/', zoo_home),
    
    path('<str:zoo_id>/species/', species_list, name='species_list'),
    path('<str:zoo_id>/species/<str:species_id>', species_page),
    
    path('<str:zoo_id>/individuals/', individuals_list, name='individuals_list'),
    path('<str:zoo_id>/individuals/<str:individual_id>', individual_page),
    
    path('<str:zoo_id>/attributes/', attribute_category_list, name='attributes_list'),
]