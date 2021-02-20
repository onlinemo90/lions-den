from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# noinspection PyUnresolvedReferences
from zoo_auth.models import Zoo

from .models import Species, Individual, Group
from .forms import SpeciesForm, IndividualForm, GroupForm, get_attributes_formset, get_new_attribute_form, get_attribute_categories_formset

# Base Views---------------------------------------------------------
class BaseZooView(LoginRequiredMixin, View):
	def dispatch(self, request, *args, **kwargs):
		""" Restrict access to view only to logged-in users with access to the specific zoo """
		# Get request and zoo_id arguments
		zoo_id = kwargs['zoo_id'] if 'zoo_id' in kwargs else args[0]
		
		# Check user permissions
		if request.user.is_authenticated and request.user.has_access(zoo_id=zoo_id):
			return super().dispatch(request, *args, **kwargs)
		return redirect('home')
	
	def get_zoo(self, zoo_id):
		return Zoo.objects.filter(id=zoo_id).get()


class SubjectPageView(BaseZooView):
	template_name = 'model_editor/subject.html'
	
	def get_subject(self, zoo_id, subject_id):
		return self.model.objects.using(zoo_id).filter(id=subject_id).get()
	
	def get_forms(self, subject, request=None):
		request_data = request.POST if request else None
		request_files = request.FILES if request else None
		
		subject_form = subject.form(data=request_data, files=request_files, instance=subject)
		attributes_formset = get_attributes_formset(data=request_data, files=request_files, subject=subject, prefix='attributes')
		new_attribute_form = get_new_attribute_form(data=request_data, subject=subject, prefix='new_attribute')
		return subject_form, attributes_formset, new_attribute_form
	
	def get(self, request, zoo_id, subject_id):
		subject = self.get_subject(zoo_id, subject_id)
		subject_form, attributes_formset, new_attribute_form = self.get_forms(subject=subject)
		return render(
			request=request,
			template_name=self.template_name,
			context={
				'zoo': self.get_zoo(zoo_id),
				'subject': subject,
				'subject_form': subject_form,
				'attributes_formset': attributes_formset,
				'new_attribute_form': new_attribute_form
			}
		)
	
	def post(self, request, zoo_id, subject_id):
		subject = self.get_subject(zoo_id, subject_id)
		subject_form, attributes_formset, new_attribute_form = self.get_forms(subject, request)
		request_valid = False
		
		if 'submit' in request.POST:
			request_valid = subject_form.is_valid() and (attributes_formset is None or attributes_formset.is_valid())
			if request_valid:
				subject_field_deletions = [field.partition('_')[2] for field in request.POST if field.startswith('DELETE-FIELD_')]
				subject_form.save(fields_to_delete=subject_field_deletions)
				if attributes_formset is not None:
					attributes_formset.save()
				subject = self.get_subject(zoo_id, subject_id)  # reload subject
		
		elif 'add_new_attribute' in request.POST:
			request_valid = new_attribute_form.is_valid()
			if request_valid:
				new_attribute_form.save()
		
		if request_valid:
			subject_form, attributes_formset, new_attribute_form = self.get_forms(subject=subject)
		
		return render(
			request=request,
			template_name=self.template_name,
			context={
				'zoo': subject.zoo,
				'subject': subject,
				'subject_form': subject_form,
				'attributes_formset': attributes_formset,
				'new_attribute_form': new_attribute_form
			}
		)


# Renderable Views---------------------------------------------------
class ZoosIndexView(LoginRequiredMixin, View):
	def get(self, request):
		if len(request.user.allowed_zoos) == 1:
			return redirect(request.user.allowed_zoos[0].id + '/')
		return render(
			request=request,
			template_name = 'model_editor/zoos_index.html',
			context={'zoos': request.user.allowed_zoos}
		)


class ZooHomeView(BaseZooView):
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name='model_editor/zoo.html',
			context={'zoo': self.get_zoo(zoo_id)}
		)


class SpeciesListView(BaseZooView):
	def render_default_page(self, request, zoo_id, new_species_form=None):
		return render(
			request=request,
			template_name='model_editor/species_list.html',
			context={
				'zoo': self.get_zoo(zoo_id),
				'subjects': Species.objects.using(zoo_id).order_by('name').all(),
				'new_subject_form': new_species_form if new_species_form else SpeciesForm(zoo_id=zoo_id)
			}
		)
	
	def get(self, request, zoo_id):
		return self.render_default_page(request, zoo_id)
	
	def post(self, request, zoo_id):
		new_species_form = SpeciesForm(data=request.POST, files=request.FILES, zoo_id=zoo_id)
		if new_species_form.is_valid():
			new_species_form.save()
			new_species_form = None
		return self.render_default_page(request, zoo_id, new_species_form=new_species_form)


class IndividualsListView(BaseZooView):
	def render_default_page(self, request, zoo_id, new_individual_form=None):
		return render(
			request=request,
			template_name='model_editor/individuals_list.html',
			context={
				'zoo': self.get_zoo(zoo_id),
				'subjects': Individual.objects.using(zoo_id).order_by('name'),
				'species_list': Species.objects.using(zoo_id).order_by('name'),
				'new_subject_form': new_individual_form if new_individual_form else IndividualForm(zoo_id=zoo_id)
			}
		)
		
	def get(self, request, zoo_id):
		if request.is_ajax():
			individuals_shown = Individual.objects.using(zoo_id).order_by('name')
			if request.GET.get('species_id'):
				individuals_shown = individuals_shown.filter(species__id=request.GET['species_id'])
			return render(
				request=request,
				template_name='model_editor/subject_table.html',
				context={'subjects': individuals_shown}
			)
		return self.render_default_page(request, zoo_id)
	
	def post(self, request, zoo_id):
		new_individual_form = IndividualForm(data=request.POST, files=request.FILES, zoo_id=zoo_id)
		if new_individual_form.is_valid():
			new_individual_form.save()
			new_individual_form = None
		return self.render_default_page(request, zoo_id, new_individual_form=new_individual_form)


class GroupsListView(BaseZooView):
	def render_default_page(self, request, zoo_id, new_group_form=None):
		return render(
			request=request,
			template_name='model_editor/groups_list.html',
			context={
				'zoo': self.get_zoo(zoo_id),
				'subjects': Group.objects.using(zoo_id).order_by('name'),
				'new_subject_form': new_group_form if new_group_form else GroupForm(zoo_id=zoo_id)
			}
		)
	
	def get(self, request, zoo_id):
		return self.render_default_page(request, zoo_id)
	
	def post(self, request, zoo_id):
		new_group_form = GroupForm(data=request.POST, files=request.FILES, zoo_id=zoo_id)
		if new_group_form.is_valid():
			new_group_form.save()
			new_group_form = None
		return self.render_default_page(request, zoo_id, new_group_form=new_group_form)


class SpeciesPageView(SubjectPageView):
	model = Species


class IndividualPageView(SubjectPageView):
	model = Individual


class GroupPageView(SubjectPageView):
	model = Group


class AttributeCategoryListView(BaseZooView):
	template_name = 'model_editor/attribute_category_list.html'
	
	def get_forms(self, zoo_id, request_data=None):
		return get_attribute_categories_formset(zoo_id=zoo_id, data=request_data)
	
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name=self.template_name,
			context={'zoo': self.get_zoo(zoo_id), 'formset': self.get_forms(zoo_id)}
		)
	
	def post(self, request, zoo_id):
		formset = self.get_forms(zoo_id, request.POST)
		if formset.is_valid():
			formset.save()
			formset = self.get_forms(zoo_id)
		return render(
			request=request,
			template_name=self.template_name,
			context={'zoo': self.get_zoo(zoo_id), 'formset': formset}
		)
