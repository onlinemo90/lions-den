from django.urls import path
from .views import zoos_index, zoo_home, species

urlpatterns = [
    path('', zoos_index),
    path('<str:zoo_id>/', zoo_home),
    path('<str:zoo_id>/<str:species_id>', species),
]