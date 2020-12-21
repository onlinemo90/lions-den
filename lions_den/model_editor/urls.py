from django.urls import path
from .views import zoo_home, species

urlpatterns = [
    path('<str:zoo_id>/', zoo_home),
    path('<str:zoo_id>/<str:species_id>', species),
]