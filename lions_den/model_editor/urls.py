from django.urls import path
from .views import ZoosIndexView, ZooHomeView, SpeciesPageView, IndividualPageView, SpeciesListView, IndividualsListView, AttributeCategoryListView

urlpatterns = [
	path('', ZoosIndexView.as_view(), name='zoo_index'),
	path('<str:zoo_id>/', ZooHomeView.as_view()),
	
	path('<str:zoo_id>/species/', SpeciesListView.as_view(), name='species_list'),
	path('<str:zoo_id>/species/<str:subject_id>', SpeciesPageView.as_view()),
	
	path('<str:zoo_id>/individuals/', IndividualsListView.as_view(), name='individuals_list'),
	path('<str:zoo_id>/individuals/<str:subject_id>', IndividualPageView.as_view()),
	
	path('<str:zoo_id>/attributes/', AttributeCategoryListView.as_view(), name='attributes_list'),
]
