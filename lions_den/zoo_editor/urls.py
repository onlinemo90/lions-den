from django.urls import path
from .views import ZoosIndexView, ZooHomeView, SpeciesPageView, IndividualPageView, GroupPageView, SpeciesListView, IndividualsListView, GroupsListView, AttributeCategoryListView, ZooLocationListView, ZooLocationPageView

urlpatterns = [
	path('', ZoosIndexView.as_view(), name='zoo_index'),
	path('<str:zoo_id>/', ZooHomeView.as_view(), name='zoo'),
	
	path('<str:zoo_id>/species/', SpeciesListView.as_view(), name='species_list'),
	path('<str:zoo_id>/species/<str:subject_id>', SpeciesPageView.as_view(), name='species_page'),
	
	path('<str:zoo_id>/individuals/', IndividualsListView.as_view(), name='individuals_list'),
	path('<str:zoo_id>/individuals/<str:subject_id>', IndividualPageView.as_view(), name='individual_page'),
	
	path('<str:zoo_id>/groups/', GroupsListView.as_view(), name='groups_list'),
	path('<str:zoo_id>/groups/<str:subject_id>', GroupPageView.as_view(), name='group_page'),
	
	path('<str:zoo_id>/attributes/', AttributeCategoryListView.as_view(), name='attribute_categories_list'),

	path('<str:zoo_id>/locations/', ZooLocationListView.as_view(), name='locations_list'),
	path('<str:zoo_id>/locations/<str:location_id>', ZooLocationPageView.as_view(), name='location'),
]
